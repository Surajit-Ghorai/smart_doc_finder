"""main application"""

import re
from google_drive import load_data
from docs_processing import (
    create_index,
    split_chunks,
    chunks_to_nodes,
    store_in_vector_database,
)
from local_embedding import load_local_embedding
from query_engine import build_query_engine
from vector_store import get_vector_database
from paths import PERSIST_DIR
import chromadb

"""
for multifolder support, passing the folder id in 
process_documents(), get_new_files(), get_all_chroma_id(), get_vector_database()
"""
# get new files
def get_new_files(docs, folder_id):
    """it takes all the files from drive and returns only new files"""
    print("checking new files.......")
    all_chroma_id = get_all_chroma_id(folder_id)
    # if vector db is empty, it means all docs are new docs
    if all_chroma_id is None:
        return docs

    new_docs = []
    for doc in docs:
        doc_id = doc.metadata["file id"]
        if doc_id not in all_chroma_id:
            new_docs.append(doc)
    if new_docs:
        print("new files found...")
    else:
        print("no new files found!!")
    return new_docs


def get_all_chroma_id(folder_id):
    """return ids of all the files embedded in the vectorstore"""
    db = chromadb.PersistentClient(path=PERSIST_DIR)
    chroma_collection = db.get_or_create_collection(folder_id)
    chroma_doc_ids = chroma_collection.get()["ids"]

    if chroma_doc_ids is None:
        return None

    all_file_id = set()
    for chroma_id in chroma_doc_ids:
        file_id = chroma_collection.get(ids=chroma_id)["metadatas"][0]["file id"]
        all_file_id.add(file_id)
    return list(all_file_id)


def retrieve_folder_id(folder_url):
    """retrieves folder id from url"""
    folder_id = re.search(r"folders/([^/?]+)", folder_url)
    if folder_id:
        return folder_id.group(1)
    else:
        return folder_url

#
def process_documents(folder_id):
    """loads and checks new documents, if new documents present, then prosses them and embed them"""
    folder_id = retrieve_folder_id(folder_id)
    # load documents
    documents = load_data(folder_id)
    print("load done...")

    if documents is None:
        return "invalid_folder"

    # check new documents
    new_docs = get_new_files(documents, folder_id)
    if new_docs is None:
        return "no_new_file"
    # chunks + nodes
    all_nodes = []
    for doc in new_docs:
        chunks = split_chunks(doc)
        for chunk in chunks:
            node = chunks_to_nodes(chunk)
            all_nodes.append(node)

    print("chunk done...")
    # embedding
    for node in all_nodes:
        embed_model = load_local_embedding()
        node_embedding = embed_model.get_text_embedding(
            node.get_content(metadata_mode="all")
        )
        node.embedding = node_embedding
    print("embedding done...")
    # storing
    store_in_vector_database(all_nodes, folder_id)
    print("storing in vector db done..")

    return "success"


def get_answer(question, folder_id):
    """retrieves context from vectordb and gets answer from LLM"""
    folder_id = retrieve_folder_id(folder_id)
    try:
        print("finding your answer..")
        # creating index
        index = create_index(get_vector_database(folder_id), load_local_embedding())
        print("fetching indexes from db..")

        # load query engine
        query_engine = build_query_engine(index)

        # Q&A
        response = query_engine.query(question)
        print("answer retrieval done..")
        # print(response)

        # metadata retrieval
        response_text = response.response
        source_nodes = response.source_nodes
        # print(response)
        if source_nodes is not None:
            metadata = source_nodes[0].metadata
        else:
            metadata = None
        print("answer done...")

        return response_text, metadata
    
    except Exception as e:
        print(e)
        return "No answer Found", None 
