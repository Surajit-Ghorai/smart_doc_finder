"""
Google drive integration:
It will fetch data from Google and will return all documents
"""

from llama_index.readers.google import GoogleDriveReader

loader = GoogleDriveReader()


def load_data(folder_id: str):
    """takes a folder id and returns all documents"""
    docs = loader.load_data(folder_id=folder_id)
    return docs
