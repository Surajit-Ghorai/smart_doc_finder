"""automation"""
import time
import schedule
from google_drive import load_google_drive
from onedriveloader import auth_onedrive, load_onedrive


# Function to check for new files and load in Google Drive
def load_files_googledrive():
    load_google_drive()

"""
def load_files_onedrive():
    access_token = auth_onedrive()
    load_google_drive(access_token)
"""

def check_and_load():
    # Schedule the check to run every specified interval
    schedule.every(0.5).minutes.do(load_files_googledrive)

    # Run the scheduler loop
    while True:
        print("...")
        schedule.run_pending()
        time.sleep(1)

check_and_load()
