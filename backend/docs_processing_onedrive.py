"""
ingestion pipeline: processing the input data
"""

import os
import re
import openai
import chromadb
from local_embedding import load_local_embedding
from dotenv import load_dotenv
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import TextNode
from llama_index.core import VectorStoreIndex
from local_llm_model import load_local_llm
from vector_store import get_vector_database
from paths import PERSIST_DIR

CHROMA_COLLECTION_NAME = "my_collection"
# loading api key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


# text splitter
text_parser = SentenceSplitter(
    chunk_size=512, chunk_overlap=64, paragraph_separator="\n\n"
)


# splitting into chunks
def split_chunks(doc):
    """splits documents into smaller chunks"""
    metadata = doc.metadata
    text_chunks = []
    cur_text_chunks = []

    cur_text_chunks = text_parser.split_text(doc.text)

    para_no = 1
    for chunk in cur_text_chunks:
        chunk_metadata = doc.metadata.copy()
        chunk_metadata["paragraph_number"] = para_no
        text_chunks.append({"text": chunk, "metadata": chunk_metadata})
        para_no += 1
        print("splitting going on..")

    return text_chunks


# converting chunks into nodes
def chunks_to_nodes(splitted_chunks):
    """converts chunks into nodes"""
    text = splitted_chunks["text"]
    metadata = splitted_chunks["metadata"]
    node = TextNode(
        text=text,
    )
    node.metadata = metadata
    return node


# store in vector_database
def store_in_vector_database(nodes, collection_name):
    """Stores nodes into vector database"""
    vector_store = get_vector_database(collection_name)
    vector_store.add(nodes)


# indexing
def create_index(vector_store, embed_model):
    """returns indexes for stored documents in vectorstore"""
    index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        embed_model=embed_model,
    )
    return index


# get new files
def get_new_files(docs, folder_id):
    """it takes all the files from drive and returns only new files"""
    print("checking new files.......")
    all_chroma_id = get_all_chroma_id(CHROMA_COLLECTION_NAME)
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


def get_all_chroma_id(CHROMA_COLLECTION_NAME):
    """return ids of all the files embedded in the vectorstore"""
    db = chromadb.PersistentClient(path=PERSIST_DIR)
    chroma_collection = db.get_or_create_collection(CHROMA_COLLECTION_NAME)
    chroma_doc_ids = chroma_collection.get()["ids"]

    if chroma_doc_ids is None:
        return None

    all_file_id = set()
    for chroma_id in chroma_doc_ids:
        file_id = chroma_collection.get(ids=chroma_id)["metadatas"][0]["file id"]
        all_file_id.add(file_id)
    return list(all_file_id)


def process_documents_onedrive(documents, folder_id):
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
    store_in_vector_database(all_nodes, "my_collection")
    print("storing in vector db done..")

    return "success"
