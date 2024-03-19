"""one drive integration"""

import os
import requests
import concurrent.futures
import docs_processing_onedrive
from dotenv import load_dotenv
from typing import Any, Dict, List, Optional
from llama_index.readers.microsoft_onedrive import OneDriveReader

load_dotenv()
ONEDRIVE_CLIENT_ID = os.getenv("ONEDRIVE_CLIENT_ID")


# my custom onedrive reader
class My_OneDriveReader(OneDriveReader):

    def __init__(
        self,
        client_id: str,
        client_secret: Optional[str] = None,
        tenant_id: str = "consumers",
        access_token: Optional[str] = None,
    ):
        super().__init__(
            client_id,
            client_secret,
            tenant_id,
        )
        self.access_token = access_token

    def _extract_metadata_for_file(self, item: Dict[str, Any]) -> Dict[str, str]:
        # Extract the required metadata for file.
        created_by = item.get("createdBy", {})
        modified_by = item.get("lastModifiedBy", {})
        return {
            "file id": item.get("id"),
            "file name": item.get("name"),
            "author": created_by.get("user", {}).get("displayName"),
            "created_by_app": created_by.get("application", {}).get("displayName"),
            "created_dateTime": item.get("createdDateTime"),
            "last_modified_by_user": modified_by.get("user", {}).get("displayName"),
            "last_modified_by_app": modified_by.get("application", {}).get(
                "displayName"
            ),
            "last_modified_datetime": item.get("lastModifiedDateTime"),
        }

    def _init_download_and_get_metadata(
        self,
        temp_dir: str,
        folder_id: Optional[str] = None,
        file_ids: Optional[List[str]] = None,
        folder_path: Optional[str] = None,
        file_paths: Optional[List[str]] = None,
        recursive: bool = False,
        mime_types: Optional[List[str]] = None,
        userprincipalname: Optional[str] = None,
    ) -> None:
        access_token = self.access_token
        is_download_from_root = True
        downloaded_files_metadata = {}
        # If a folder_id is provided, download files from the folder
        if folder_id:
            is_download_from_root = False
            folder_metadata = self._connect_download_and_return_metadata(
                access_token,
                temp_dir,
                folder_id,
                recursive,
                mime_types=mime_types,
                userprincipalname=userprincipalname,
            )
            downloaded_files_metadata.update(folder_metadata)

        # Download files using the provided file IDs
        if file_ids:
            is_download_from_root = False
            for file_id in file_ids or []:
                item = self._get_items_in_drive_with_maxretries(
                    access_token,
                    file_id,
                    userprincipalname=userprincipalname,
                    isFile=True,
                )
                file_metadata = self._check_approved_mimetype_and_download_file(
                    item, temp_dir, mime_types
                )
                downloaded_files_metadata.update(file_metadata)

        # If a folder_path is provided, download files from the folder
        if folder_path:
            is_download_from_root = False
            folder_metadata = self._connect_download_and_return_metadata(
                access_token,
                temp_dir,
                folder_path,
                recursive,
                mime_types=mime_types,
                userprincipalname=userprincipalname,
                isRelativePath=True,
            )
            downloaded_files_metadata.update(folder_metadata)

        # Download files using the provided file paths
        if file_paths:
            is_download_from_root = False
            for file_path in file_paths or []:
                item = self._get_items_in_drive_with_maxretries(
                    access_token,
                    file_path,
                    userprincipalname=userprincipalname,
                    isFile=True,
                    isRelativePath=True,
                )
                file_metadata = self._check_approved_mimetype_and_download_file(
                    item, temp_dir, mime_types
                )
                downloaded_files_metadata.update(file_metadata)

        if is_download_from_root:
            # download files from root folder
            root_folder_metadata = self._connect_download_and_return_metadata(
                access_token,
                temp_dir,
                "root",
                recursive,
                mime_types=mime_types,
                userprincipalname=userprincipalname,
            )
            downloaded_files_metadata.update(root_folder_metadata)

        return downloaded_files_metadata

    def get_all_folder_ids(self):
        access_token = self.access_token
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        response = requests.get(
            "https://graph.microsoft.com/v1.0/me/drive/root/children", headers=headers
        )
        response_data = response.json()

        folder_ids = []
        for item in response_data.get("value", []):
            if item.get("folder"):
                folder_ids.append(item["id"])
                # Call a recursive function to get all subfolder IDs
                folder_ids.extend(self.get_all_subfolder_ids(item["id"], headers))

        return folder_ids

    def get_all_subfolder_ids(self, folder_id, headers):
        folder_ids = []
        response = requests.get(
            f"https://graph.microsoft.com/v1.0/me/drive/items/{folder_id}/children",
            headers=headers,
        )
        response_data = response.json()

        for item in response_data.get("value", []):
            if item.get("folder"):
                folder_ids.append(item["id"])
                # Recursively call to get subfolder IDs
                folder_ids.extend(self.get_all_subfolder_ids(item["id"], headers))

        return folder_ids

# authenticate onedrive and get access token
def auth_onedrive():
    access_token = OneDriveReader(
        client_id=ONEDRIVE_CLIENT_ID
    )._authenticate_with_msal()
    return access_token

# loader
def load_data_using_onedrive_reader(folder_id: str, access_token:str):
    """takes a folder id and returns all documents"""
    loader = My_OneDriveReader(client_id=ONEDRIVE_CLIENT_ID, access_token=access_token)
    try:
        docs = loader.load_data(
            folder_id=folder_id,
            recursive=False,
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
    except Exception as e:
        print(e)
        docs = None
    return docs


# parallel load
def load_documents_parallely(folder_ids, access_token):
    print("downloading...")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Download files for each folder concurrently
        futures = [
            executor.submit(call_loader, folder_id, access_token)
            for folder_id in folder_ids
        ]

        # Wait for all tasks to complete
        concurrent.futures.wait(futures)


# dfbh
def call_loader(folder_id, access_token):
    print("stage 2...")
    doc = load_data_using_onedrive_reader(folder_id, access_token)
    print(f"data loaded: {folder_id} ...!!!")
    #print(doc)
    response = docs_processing_onedrive.process_documents_onedrive(doc, folder_id)
    print(response)


# main function
def load_onedrive(access_token):
    loader = My_OneDriveReader(client_id=ONEDRIVE_CLIENT_ID, access_token=access_token)
    folder_ids = loader.get_all_folder_ids()
    print(f"folder ids: {folder_ids}")
    load_documents_parallely(folder_ids, access_token)


# sample usage
access_token = auth_onedrive()
load_onedrive(access_token)
