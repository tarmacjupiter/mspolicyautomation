import os
import time
import subprocess
from GetFiles import GetFiles

batch_size = 10  # You can change the batch size here

files = GetFiles.get_test_files()
total_files = len(files["value"])

# Loop through the total files in batch sizes
for i in range(0, total_files, batch_size):
    start_index = i
    end_index = min(i + batch_size, total_files)
    
    print(f"Starting batch from {start_index} to {end_index}...")
    
    # Call the original script with the start and end indices as arguments
    result = subprocess.run(
        ["python", "main.py", str(start_index), str(end_index)]
    )
    
    # Check if the subprocess call was successful
    if result.returncode != 0:
        print(f"Error occurred in batch {start_index} to {end_index}")
    
    print(f"Finished batch from {start_index} to {end_index}. Waiting 10 seconds...")
    time.sleep(10)
