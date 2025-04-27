import os
import time
import psutil
import gc
import numpy as np
from datetime import datetime

def get_memory_usage():
    """Return the memory usage in MB."""
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    return mem_info.rss / (1024 * 1024)  # Convert to MB

def format_size(size_bytes):
    """Format size in bytes to human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0 or unit == 'TB':
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0

def test_ram(max_percent=80, step_size_mb=256, delay_between_steps=1):
    """
    Test RAM by incrementally allocating memory.
    
    Args:
        max_percent: Maximum percentage of total RAM to use
        step_size_mb: Size of each memory allocation step in MB
        delay_between_steps: Delay between allocation steps in seconds
    """
    # Get system memory information
    total_ram = psutil.virtual_memory().total
    total_ram_mb = total_ram / (1024 * 1024)
    max_ram_mb = total_ram_mb * (max_percent / 100)
    
    print(f"RAM Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total System RAM: {format_size(total_ram)}")
    print(f"Will use up to {max_percent}% of RAM ({format_size(max_ram_mb * 1024 * 1024)})")
    print(f"Step size: {step_size_mb} MB")
    print("-" * 60)
    print("| Step | Allocated | Total Usage | Allocation Time | Access Time |")
    print("-" * 60)
    
    # List to store allocated arrays
    arrays = []
    step = 1
    
    try:
        # Continue allocating memory until we reach the limit
        while get_memory_usage() < max_ram_mb:
            # Allocate memory
            alloc_start = time.time()
            # Create a numpy array of the specified size
            arr = np.ones((step_size_mb * 1024 * 1024) // 8, dtype=np.float64)
            arrays.append(arr)
            alloc_time = time.time() - alloc_start
            
            # Access the memory to ensure it's actually allocated
            access_start = time.time()
            # Perform a simple operation to ensure memory is accessed
            _ = np.sum(arr[::1000000])
            access_time = time.time() - access_start
            
            current_usage = get_memory_usage()
            
            # Print status
            print(f"| {step:4d} | {step * step_size_mb:6d} MB | "
                  f"{current_usage:8.2f} MB | "
                  f"{alloc_time*1000:8.2f} ms | {access_time*1000:8.2f} ms |")
            
            step += 1
            time.sleep(delay_between_steps)
    
    except MemoryError:
        print("\nMemory Error encountered! Your system ran out of available RAM.")
    except KeyboardInterrupt:
        print("\nTest stopped by user.")
    except Exception as e:
        print(f"\nError: {str(e)}")
    finally:
        # Calculate statistics
        final_usage = get_memory_usage()
        usage_percent = (final_usage / total_ram_mb) * 100
        
        print("-" * 60)
        print(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Final memory usage: {format_size(final_usage * 1024 * 1024)} ({usage_percent:.2f}% of total)")
        print(f"Total steps completed: {step - 1}")
        print(f"Total memory allocated: {format_size((step - 1) * step_size_mb * 1024 * 1024)}")
        
        # Clean up
        print("\nCleaning up allocated memory...")
        del arrays
        gc.collect()
        print(f"Memory after cleanup: {format_size(get_memory_usage() * 1024 * 1024)}")

if __name__ == "__main__":
    print("RAM Testing Tool")
    print("=" * 50)
    print("This script will incrementally allocate memory to test your RAM.")
    print("Press Ctrl+C at any time to stop the test.\n")
    
    try:
        max_percent = float(input("Maximum % of RAM to use (default 80): ") or 80)
        step_size = int(input("Step size in MB (default 256): ") or 256)
        delay = float(input("Delay between steps in seconds (default 1): ") or 1)
        
        test_ram(max_percent=max_percent, step_size_mb=step_size, delay_between_steps=delay)
    except ValueError:
        print("Invalid input. Using default values.")
        test_ram()
