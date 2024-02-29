"""main application"""

from google_drive import load_data
from docs_processing import create_index, split_chunks, chunks_to_nodes, store_in_vector_database
from local_embedding import load_local_embedding
from query_engine import build_query_engine
from vector_store import get_vector_database
from constants import FOLDER_ID
from paths import PERSIST_DIR
import chromadb


# get new files
def get_new_files(docs):
    all_chroma_id = get_all_chroma_id()
    all_doc_id = []
    new_docs = []
    for doc in docs:
        doc_id = doc.metadata["file id"]
        all_doc_id.append(doc_id)
        if doc_id not in all_chroma_id:
            new_docs.append(doc)

    # deleting deleted files from chroma
    for chroma_id in all_chroma_id:
        if chroma_id not in all_doc_id:
            delete_chroma_doc(chroma_id)

    return new_docs


#
def get_all_chroma_id():
    db = chromadb.PersistentClient(path=PERSIST_DIR)
    chroma_collection = db.get_or_create_collection("my_collection")
    chroma_doc_ids = chroma_collection.get()["ids"]

    all_file_id = set()
    for chroma_id in chroma_doc_ids:
        file_id = chroma_collection.get(ids=chroma_id)["metadatas"][0]["file id"]
        all_file_id.add(file_id)
    return list(all_file_id)


#
def delete_chroma_doc(id):
    db = chromadb.PersistentClient(path=PERSIST_DIR)
    chroma_collection = db.get_or_create_collection("my_collection")
    chroma_doc_ids = chroma_collection.get()["ids"]

    for chroma_id in chroma_doc_ids:
        file_id = chroma_collection.get(ids=chroma_id)["metadatas"][0]["file id"]
        if file_id == id:
            chroma_collection.delete(ids=chroma_id)


#
def get_answer(question):
    # load documents
    documents = load_data(FOLDER_ID)
    print(len(documents), " docs")

    # check new documents
    new_docs = get_new_files(documents)

    # chunks + nodes
    all_nodes = []
    for doc in new_docs:
        chunks = split_chunks(doc)
        for chunk in chunks:
            node = chunks_to_nodes(chunk)
            all_nodes.append(node)

    # embedding
    for node in all_nodes:
        embed_model = load_local_embedding()
        node_embedding = embed_model.get_text_embedding(
            node.get_content(metadata_mode="all")
        )
        node.embedding = node_embedding

    # storing
    store_in_vector_database(all_nodes)

    # creating index
    index = create_index(get_vector_database(), load_local_embedding())

    # load query engine
    query_engine = build_query_engine(index)

    # Q&A
    response = query_engine.query(question)

    # metadata retrieval
    response_text = response.response
    metadata = response.source_nodes[0].metadata

    return response_text,metadata
