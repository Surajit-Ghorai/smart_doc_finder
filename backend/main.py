"""main application"""
from google_drive import load_data
from docs_processing import build_pipeline, create_index
from local_embedding import load_local_embedding
from query_engine import build_query_engine
from vector_store import get_vector_database
from constants import FOLDER_ID

def get_answer(question):
    # load documents
    documents = load_data(FOLDER_ID)

    # building ingestion pipeline and processing input data
    pipeline = build_pipeline()

    # nodes
    nodes = pipeline.run(documents=documents, num_workers=None)

    # index documents and store in vector database
    index = create_index(get_vector_database(), load_local_embedding())

    # load query engine
    query_engine = build_query_engine(index)
    # query_engine = index.as_query_engine()

    # Q&A
    response = query_engine.query(question)
    answer = response.response
    file_name = response.source_nodes[0].metadata["file name"]
    page_number = response.source_nodes[0].metadata["page_label"]
    my_response = [answer, file_name, page_number]
    return my_response

# print(get_answer('title of the story'))
