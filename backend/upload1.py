'''uploading large files'''
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

#from upload_to_drive import authenticate
SCOPES = ["https://www.googleapis.com/auth/drive"]
FILE_PATH = r"C:\Users\promact\Downloads\bear_story.pdf"
FOLDER_ID = "1hzk7y9TZ0lCRhaIdOOLkoJRblduoIQ3p"

def upload_with_conversion():
    """Upload file with conversion
    Returns: ID of the file uploaded
    """
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

    try:
        # create drive api client
        service = build("drive", "v3", credentials=creds)

        file_metadata = {
            "name": "bear story",
        }
        media = MediaFileUpload(FILE_PATH, resumable=True)
        # pylint: disable=maybe-no-member
        file = (
            service.files()
            .create(body=file_metadata, media_body=media, fields="id")
            .execute()
        )
        print(f'File with ID: "{file.get("id")}" has been uploaded.')

    except HttpError as error:
        print(f"An error occurred: {error}")
        file = None

    return file.get("id")


if __name__ == "__main__":
    upload_with_conversion()