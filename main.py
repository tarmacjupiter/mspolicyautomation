from GetFiles import GetFiles, link, get_file_extension
import requests
import re
import time
import os
from dotenv import load_dotenv
import json
from colorama import Fore, Back, Style, init
from itertools import islice
import sys

load_dotenv()

# Check and parse command-line arguments
if len(sys.argv) != 3:
    print("Usage: python send_files.py <start_index> <end_index>")
    sys.exit(1)

start_index = int(sys.argv[1])
end_index = int(sys.argv[2])

# Make a files class
files = GetFiles.get_test_files()
all_files = files["value"]

# Validate indices
if start_index >= len(all_files) or end_index > len(all_files):
    print(f"Invalid range! Total files: {len(all_files)}")
    sys.exit(1)

# Extract the batch of files to be sent
batch = list(islice(all_files, start_index, end_index))

# This url is where to send the files to!
post_url = f"https://graph.microsoft.com/v1.0/teams/{os.getenv('team_id')}/channels/{os.getenv('channel_id')}/messages"
headers = {
    "Authorization": f"Bearer {os.getenv('bearer')}",
    "Content-Type": "application/json"
}

def process_batch(batch):
    for file in batch:
        try:
            etag = file.get("eTag", "")
            guid_match = re.search(r'\{(.*?)\}', etag)
            file_guid = guid_match.group(1) if guid_match else None
            if not file_guid:
                print(f"**ERROR**, could not extract valid GUID for file: {file['name']}")
                continue
            
            file_extension = get_file_extension(file['name'])
            content_url = file.get("@microsoft.graph.downloadUrl", file.get("webUrl", ""))
            
            if not content_url.lower().endswith(file_extension.lower()):
                content_url = f"{content_url}{file_extension}"
            
            attachment = {
                "id": file_guid,
                "contentType": "reference",
                "contentUrl": content_url,
                "name": file["name"]
            }
            
            payload = {
                "body": {
                    "contentType": "html",
                    "content": f"Sending {attachment['name']}... <attachment id=\"{file_guid}\"></attachment>"
                },
                "attachments": [attachment]
            }
            
            init(autoreset=True)
            print(f"{Fore.GREEN}{Style.BRIGHT}Sending file: {Back.CYAN}{file['name']}")
            print()
            print(f"Content URL: {Style.DIM}{link(content_url, file['name'])}")
            
            response = requests.post(post_url, headers=headers, json=payload)
            
            # Attempt to pretty-print the response if it's JSON
            try:
                response_json = response.json()
                formatted_json = json.dumps(response_json, indent=2)
                print()
                print(f"{Fore.GREEN}{Style.BRIGHT}Response (formatted JSON):{Style.RESET_ALL}\n{Fore.BLUE}{Style.BRIGHT}{formatted_json}")
                print()
            except json.JSONDecodeError:
                print(f"{Fore.RED}{Style.BRIGHT}Response (non-JSON):{Style.RESET_ALL} {response.text}")
            
            print("-" * 50)
            time.sleep(3)
        except Exception as e:
            print(f"An error occurred while processing file {file['name']}: {e}")
            print(f"Exception type: {type(e).__name__}")
            import traceback
            traceback.print_exc()

# Process the batch
print(f"Processing files from {start_index} to {end_index}...")
process_batch(batch)