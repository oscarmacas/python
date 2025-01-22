import csv
import os
import tempfile
import shutil

def read_file_with_encoding(file_path, encodings=['utf-8', 'latin-1', 'cp1252']):
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read(), encoding
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError(f"Unable to decode the file {file_path} with any of the provided encodings.")

def read_codlookup():
    lookup = {}
    file_path = r'C:\script\lib\codlookup.csv'
    content, encoding = read_file_with_encoding(file_path)
    reader = csv.reader(content.splitlines())
    for row in reader:
        if len(row) >= 2:
            lookup[row[0]] = row[1]
    return lookup

def safe_int(value):
    try:
        return int(value)
    except ValueError:
        return 0

def process_csv(filename, lookup):
    data = {}
    content, encoding = read_file_with_encoding(filename)
    reader = csv.reader(content.splitlines())
    for row in reader:
        if len(row) >= 2:
            code, quantity = row[:2]
            if code in data:
                data[code] += safe_int(quantity)
            else:
                data[code] = safe_int(quantity)
    
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, newline='', encoding=encoding)
    with temp_file as temp:
        for code, quantity in data.items():
            description = lookup.get(code, "error")
            temp.write(f'{code},{quantity},"{description}"\n')
    
    shutil.move(temp_file.name, filename)
    print(f"Processed {filename}")

def main():
    lookup = read_codlookup()
    for filename in os.listdir('.'):
        if filename.endswith('.csv') and filename != 'codlookup.csv':
            process_csv(filename, lookup)

if __name__ == "__main__":
    main()

# Ejecutar el script
main()
