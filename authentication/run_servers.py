import os
import uvicorn
import sys
import threading
import schedule
import time


backend_dir = os.path.abspath("./backend")
sys.path.insert(1, backend_dir)
import google_drive

# import track
def load_files_googledrive():
    google_drive.load_google_drive()


def run_api_server():
    print("api")
    uvicorn.run("my_api:app", host="127.0.0.1", port=8000, reload=False)
    # subprocess.run(["uvicorn", "my_api:app", "--host", "127.0.0.1", "--port", "8000", "--reload=False"])
    time.sleep(10)


def run_new_file_loader():
    # Schedule the check to run every specified interval
    schedule.every(10).minutes.do(load_files_googledrive)

    # Run the scheduler loop
    while True:
        print("...")
        schedule.run_pending()
        time.sleep(10)


if __name__ == "__main__":

    # Create processes for each function
    process1 = threading.Thread(target=run_api_server)
    process2 = threading.Thread(target=run_new_file_loader)

    # Start both processes
    process1.start()
    process2.start()

    # Wait for both processes to finish
    process1.join()
    process2.join()
