"""
vector datastore
"""

import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore

from paths import PERSIST_DIR


# vector database
# now creating collections for each folder id
def get_vector_database(collection_name):
    """returns vectorstore"""
    db = chromadb.PersistentClient(path=PERSIST_DIR)
    chroma_collection = db.get_or_create_collection(collection_name)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

    return vector_store
