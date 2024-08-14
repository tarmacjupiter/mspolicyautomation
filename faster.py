import os
import re
import asyncio
import aiohttp
from GetFiles import GetFiles, link
from dotenv import load_dotenv
from colorama import Fore, Style, init
import asyncio
import random
from aiohttp import ClientResponseError

load_dotenv()

async def send_file(session, file, post_url, headers):
    max_retries = 5
    base_delay = 1

    for attempt in range(max_retries):
        try:
            etag = file.get("eTag", "")
            guid_match = re.search(r'\{(.*?)\}', etag)
            file_guid = guid_match.group(1) if guid_match else None
            if not file_guid:
                print(f"**ERROR**, could not extract valid GUID for file: {file['name']}")
                return

            _, file_extension = os.path.splitext(file['name'])
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

            print(f"{Fore.GREEN}{Style.BRIGHT}Sending file: {file['name']}")
            
            async with session.post(post_url, headers=headers, json=payload) as response:
                response.raise_for_status()
                response_text = await response.text()
                print(f"{Fore.GREEN}{Style.BRIGHT}Response:{Style.RESET_ALL} {Style.BRIGHT}{Fore.BLUE}{response_text[:100]}...")
                return  # Successful, exit the function

        except ClientResponseError as e:
            if e.status == 412:  # PreconditionFailed
                delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                print(f"{Fore.YELLOW}PreconditionFailed for {file['name']}. Retrying in {delay:.2f} seconds...")
                await asyncio.sleep(delay)
            elif e.status == 429:  # TooManyRequests
                delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                print(f"{Fore.RED}TooManyRequests error. Pausing for {delay:.2f} seconds...")
                await asyncio.sleep(delay)
            else:
                print(f"{Fore.RED}Error sending {file['name']}: {e}")
                return
        except Exception as e:
            print(f"{Fore.RED}Unexpected error sending {file['name']}: {e}")
            return

    print(f"{Fore.RED}Failed to send {file['name']} after {max_retries} attempts.")

async def main():
    init(autoreset=True)
    files = GetFiles.get_test_files()
    post_url = f"https://graph.microsoft.com/v1.0/teams/{os.getenv('team_id')}/channels/{os.getenv('channel_id')}/messages"
    headers = {
        "Authorization": f"Bearer {os.getenv('bearer')}",
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        tasks = [send_file(session, file, post_url, headers) for file in files["value"]]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"An error occurred: {e}")
        print(f"Exception type: {type(e).__name__}")
        import traceback
        traceback.print_exc()

    print()
    input("Press Enter to exit!\n")
    print("Thank you!")