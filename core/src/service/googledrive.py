def get_size_format(b, factor=1024, suffix="B"):
    """
    Scale bytes to its proper byte format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if b < factor:
            return f"{b:.2f}{unit}{suffix}"
        b /= factor
    return f"{b:.2f}Y{suffix}"

def list_files(items):
    """given items returned by Google Drive API, prints them in a tabular way"""
    if not items:
        # empty drive
        print('No files found.')
        return []
    rows = []
    for item in items:
        # get the File ID
        id = item["id"]
        # get the name of file
        name = item["name"]
        try:
            # parent directory ID
            parents = item["parents"]
        except:
            # has no parrents
            parents = "N/A"
        try:
            # get the size in nice bytes format (KB, MB, etc.)
            size = get_size_format(int(item["size"]))
        except:
            # not a file, may be a folder
            size = "N/A"
        # get the Google Drive type of file
        mime_type = item["mimeType"]
        # get last modified date time
        modified_time = item["modifiedTime"]
        # append everything to the list
        rows.append((id, name, parents, size, mime_type, modified_time))
    # table = tabulate(rows, headers=["ID", "Name", "Parents", "Size", "Type", "Modified Time"])
    # print(table)
    return rows

import os
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials


class GoogleDriveService:

    def __init__(self):
        self._SCOPES=['https://www.googleapis.com/auth/drive']
        env_path = os.path.dirname(__file__)
        _base_path = f"{env_path}/../../.keys"
        _credential_path=os.path.join(_base_path, 'drive_master.json')
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = _credential_path
        self.service = self.__build()
        return

    def __build(self):
        creds = ServiceAccountCredentials.from_json_keyfile_name(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"), self._SCOPES)
        service = build('drive', 'v3', credentials=creds)
        return service