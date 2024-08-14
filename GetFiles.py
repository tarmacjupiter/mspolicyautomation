import requests
import os
from dotenv import load_dotenv 

load_dotenv()

class GetFiles:
    """
    GetFiles (class): 
        A class that finds all the files in a folder and returns the response from that folder
        in a json object
    """
    def __init__(self):
        """
        Instantiating the "all_files" variable
        """
        self.all_files = None

    def get_test_files():
        """
        Sends a GET request to the Graph explorer API to get all the files in a folder

        Returns:
            json/object: a json object of all the files in that folder/subfolder
        """
        # for the url, get the drive id and put into the .env
        url = f"https://graph.microsoft.com/v1.0/drives/{os.getenv('drive_id')}/root:/General/Test:/children" # change location of where to send files here!
        headers = {
            "Authorization": f"Bearer {os.getenv('bearer')}",
            "Content-Type": "application/json"
        }

        response = requests.request("GET", url=url, headers=headers)

        return response.json()

def link(uri, label=None):
    if label is None:
        label = uri
    parameters = ''

    escape_mask = '\033]8;{};{}\033\\{}\033]8;;\033\\'

    return escape_mask.format(parameters, uri, label)


def get_file_extension(filename):
    """
    Get the file extension of a file

    Args:
        filename (string): the file name

    Returns:
        string: returns a string of the file extension
    """
    return os.path.splitext(filename)[1]