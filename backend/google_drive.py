"""
Google drive integration:
It will fetch data from Google and will return all documents
"""

from llama_index.readers.google import GoogleDriveReader
from typing import Tuple

import os
from pathlib import Path
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from pydrive.drive import GoogleDrive
import concurrent.futures
import docs_processing_onedrive


SCOPES = ["https://www.googleapis.com/auth/drive"]


class My_GoogleDriveReader(GoogleDriveReader):
    """overriding the GoogleDriveReader class to enable oauth instead of service account"""
    def __init__(
        self,
        credentials_path: str = "my_cred.json",
        token_path: str = "token.json",
        pydrive_creds_path: str = "creds.txt",
    ) -> None:
        """Initialize with parameters."""
        super().__init__(
            credentials_path,
            token_path,
            pydrive_creds_path,
        )
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.pydrive_creds_path = pydrive_creds_path

        self._creds = None
        self._drive = None

        self._mimetypes = {
            "application/vnd.google-apps.document": {
                "mimetype": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "extension": ".docx",
            },
            "application/vnd.google-apps.spreadsheet": {
                "mimetype": (
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                ),
                "extension": ".xlsx",
            },
            "application/vnd.google-apps.presentation": {
                "mimetype": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                "extension": ".pptx",
            },
        }

    def _get_credentials(self) -> Tuple[Credentials, GoogleDrive]:
        """overriding the authentication function to get credential"""
        from google_auth_oauthlib.flow import InstalledAppFlow

        creds = None

        if Path(self.token_path).exists():
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(self.token_path, "w", encoding="utf-8") as token:
                token.write(creds.to_json())

        # self._creds = creds
        return creds, None

    def get_all_folderids(self, folder_id=None, creds=None, processed_folders=set()):
        """returns a list of all folder_ids"""
        if creds == None:
            creds, _ = self._get_credentials()
        service = build("drive", "v3", credentials=creds)
        folder_ids = []
        results = (
            service.files()
            .list(
                q=(
                    f"mimeType='application/vnd.google-apps.folder'"
                    + (f" and '{folder_id}' in parents" if folder_id else "")
                ),
                fields="nextPageToken, files(id)",
            )
            .execute()
        )
        items = results.get("files", [])

        if not items:
            return folder_ids

        for item in items:
            if item["id"] not in processed_folders:
                folder_ids.append(item["id"])
                processed_folders.add(item["id"])
                folder_ids.extend(
                    self.get_all_folderids(item["id"], creds, processed_folders)
                )

        return folder_ids

    def get_root_folderid(self, creds=None):
        """returns root folder_id"""
        if creds == None:
            creds, _ = self._get_credentials()
        service = build("drive", "v3", credentials=creds)
        root_id = None
        results = (
            service.files()
            .list(
                fields="nextPageToken, files(id, parents)",
                q="'root' in parents",
            )
            .execute()
        )
        files = results.get("files", [])
        # print("files: ", files)
        if files:
            file = files[0]
            root_id = file["parents"]
        return root_id


# authenticate google drive and get access token
def auth_googledrive():
    loader = My_GoogleDriveReader()
    access_token, _ = loader._get_credentials()
    return access_token


def load_data(folder_id):
    """takes a folder id and returns all documents"""
    loader = My_GoogleDriveReader()
    docs = loader.load_data(
        folder_id=folder_id,
        mime_types=[
            "application/pdf",
            "application/json",
            "text/plain",
            "text/markdown",
            "text/html",
            "text/css",
            "text/javascript",
            "text/x-python",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "application/vnd.ms-powerpoint",
            "application/msword",
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ],
    )
    return docs


# parallel load
def load_documents_parallely(folder_ids):
    """runs data loading and processing for each folder in a different thread"""
    print("downloading...")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Download files for each folder concurrently
        futures = [executor.submit(call_loader, folder_id) for folder_id in folder_ids]

        # Wait for all tasks to complete
        concurrent.futures.wait(futures)


def call_loader(folder_id):
    """loads and processes data"""
    print("stage 2...")
    doc = load_data(folder_id)
    print(f"data loaded: {folder_id} ...!!!")
    # print(doc)
    response = docs_processing_onedrive.process_documents_onedrive(doc, folder_id)
    print(response)


# main function
def load_google_drive():
    loader = My_GoogleDriveReader()
    # folder_ids = loader.get_all_folderids()
    # print(f"folder ids: {folder_ids}")
    root_id = loader.get_root_folderid()
    print(f"file ids: {root_id}")
    load_documents_parallely(root_id)

#load_google_drive()
#print(auth_googledrive())
