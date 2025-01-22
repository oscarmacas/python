import pandas as pd
import glob
import os
from collections import defaultdict

def merge_csv_files():
    # Get all CSV files in current directory
    csv_files = glob.glob('*.csv')
    
    if not csv_files:
        print("No CSV files found in current directory")
        return
    
    # List to store all dataframes
    all_dfs = []
    # Dictionary to track source file for each code
    code_sources = defaultdict(list)
    # Dictionary to track original quantities before summing
    original_quantities = defaultdict(list)
    
    # Read each CSV file
    for file in csv_files:
        try:
            # Read CSV without headers
            df = pd.read_csv(file, header=None, on_bad_lines='skip')
            
            # Rename existing columns (even if there are only 2)
            column_names = {0: 'codes', 1: 'quantity'}
            if len(df.columns) >= 3:
                column_names[2] = 'descriptions'
            
            # Rename only the columns that exist
            df = df.rename(columns=column_names)
            
            # If 'descriptions' column doesn't exist, add it with empty values
            if 'descriptions' not in df.columns:
                df['descriptions'] = ''
            
            # Track source file and quantities for each code
            for _, row in df.iterrows():
                code_sources[row['codes']].append(file)
                original_quantities[row['codes']].append((file, row['quantity']))
            
            all_dfs.append(df)
            print(f"\nSuccessfully read file: {file}")
            print(f"Number of rows: {len(df)}")
            
        except Exception as e:
            print(f"Error reading file {file}: {str(e)}")
            continue
    
    if not all_dfs:
        print("No valid dataframes to merge")
        return
    
    # Combine all dataframes
    merged_df = pd.concat(all_dfs, ignore_index=True)
    
    # Convert quantity to numeric, replacing errors with 0
    merged_df['quantity'] = pd.to_numeric(merged_df['quantity'], errors='coerce').fillna(0)
    
    # Group by 'codes' and aggregate
    result = merged_df.groupby('codes').agg({
        'quantity': 'sum',
        'descriptions': lambda x: next((s for s in x if s), ''),
        **{col: 'first' for col in merged_df.columns[3:]}
    }).reset_index()
    
    # Print detailed merge information
    print("\n=== DETAILED MERGE INFORMATION ===")
    for code in result['codes']:
        files = code_sources[code]
        quantities = original_quantities[code]
        
        if len(files) == 1:
            print(f"\nCode {code} appears only in {files[0]}")
            print(f"Quantity: {quantities[0][1]}")
        else:
            print(f"\nCode {code} appears in multiple files:")
            print("Original quantities:")
            for file, qty in quantities:
                print(f"  - {file}: {qty}")
            print(f"Final summed quantity: {result.loc[result['codes'] == code, 'quantity'].values[0]}")
    
    # Save the result
    output_file = 'merged_result.csv'
    result.to_csv(output_file, index=False, header=False)
    print(f"\nFiles merged successfully. Result saved as: {output_file}")
    print(f"Total rows in original files: {len(merged_df)}")
    print(f"Total rows after merging: {len(result)}")
    print(f"Number of codes that appeared in multiple files: {sum(1 for codes in code_sources.values() if len(codes) > 1)}")

if __name__ == "__main__":
    merge_csv_files()
