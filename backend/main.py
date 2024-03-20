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


def get_answer(question, folder_id):
    """retrieves context from vectordb and gets answer from LLM"""
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
