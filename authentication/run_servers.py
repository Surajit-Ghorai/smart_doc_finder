import os
import uvicorn
import sys
import threading
import multiprocessing
import time
import concurrent.futures
import subprocess

backend_dir = os.path.abspath("./backend")
sys.path.insert(1, backend_dir)

import track


def run_api_server():
    #uvicorn.run("my_api:app", host="127.0.0.1", port=8000, reload=False)
    subprocess.run(["uvicorn", "my_api:app", "--host", "127.0.0.1", "--port", "8000", "--reload=False"])


def run_new_file_loader():
    track.check_and_load()


if __name__ == "__main__":
    
    # Create processes for each function
    process1 = multiprocessing.Process(target=run_api_server)
    process2 = multiprocessing.Process(target=run_new_file_loader)

    # Start both processes
    process1.start()
    process2.start()

    # Wait for both processes to finish
    process1.join()
    process2.join()
    '''
    with concurrent.futures.ProcessPoolExecutor(max_workers=2) as executor:
        # Submit both functions for execution
        future1 = executor.submit(run_api_server)
        future2 = executor.submit(run_new_file_loader)

        # Wait for both functions to complete
        concurrent.futures.wait([future1, future2])
    '''