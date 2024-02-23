'''for testing upload into google drive'''
import os.path
import io

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from googleapiclient.http import MediaFileUpload

from googleapiclient.http import MediaIoBaseDownload

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive"]

FILE_PATH = r"C:\Users\promact\Downloads\bear_story.pdf"
FILE_PATH2 = r"C:\Users\promact\Downloads\lion_rabbit_story.pdf"
FOLDER_ID = ["1hzk7y9TZ0lCRhaIdOOLkoJRblduoIQ3p"]


def authenticate():
    """authenticate user's google drive account"""
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=8000)
            # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds

def upload_file(file_path):
    """Upload file with conversion
    Returns: ID of the file uploaded
    """
    creds = authenticate()

    try:
        # create drive api client
        service = build("drive", "v3", credentials=creds)

        file_metadata = {
            "name": "bear story 2",
            'parents': FOLDER_ID
        }
        media = MediaFileUpload(file_path, resumable=True)
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

def download_files(real_file_id):
    """Get files from google drive"""
    creds = authenticate()

    try:
        # create drive api client
        service = build("drive", "v3", credentials=creds)

        file_id = real_file_id
        request = service.files().get_media(fileId=file_id)
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}.")

    except HttpError as error:
        print(f"An error occurred: {error}")
        file = None

    return file

def search_file():
  """Search file in drive location"""
  creds= authenticate()

  try:
    # create drive api client
    service = build("drive", "v3", credentials=creds)
    files = []
    page_token = None
    while True:
      # pylint: disable=maybe-no-member
      response = (
          service.files()
          .list(
              q="mimeType='image/jpeg'",
              spaces="drive",
              fields="nextPageToken, files(id, name)",
              pageToken=page_token,
          )
          .execute()
      )
      for file in response.get("files", []):
        # Process change
        print(f'Found file: {file.get("name")}, {file.get("id")}')
      files.extend(response.get("files", []))
      page_token = response.get("nextPageToken", None)
      if page_token is None:
        break

  except HttpError as error:
    print(f"An error occurred: {error}")
    files = None

  return files

def search_files2():
    '''dd'''
    creds= authenticate()

    try:
        service = build("drive", "v3", credentials=creds)
        results = (
            service.files()
            .list(q = "'" + FOLDER_ID[0] + "' in parents", pageSize=10, fields="nextPageToken, files(id, name)")
            .execute()
        )
        items = results.get("files", [])

        return items

    except HttpError as error:
        print(f"An error occurred: {error}")
        files = None

    return files

def main():
    '''main function'''
    #creds = authenticate()
    #uploaded_file = upload_file(FILE_PATH)
    files = search_files2()
    if not files:
        print("No files found.")
    else:
        print("Files:")
        for item in files:
            print(f"{item['name']} : {item['id']}")

if __name__ == "__main__":
    main()
