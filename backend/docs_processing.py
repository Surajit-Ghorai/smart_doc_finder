"""
ingestion pipeline: processing the input data
"""
from llama_index.core import Document
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.extractors import TitleExtractor
from llama_index.core.ingestion import IngestionPipeline, IngestionCache
from llama_index.core import VectorStoreIndex
from llama_index.core.storage.docstore import SimpleDocumentStore

from local_embedding import load_local_embedding
from vector_store import get_vector_database
from constants import PIPELINE_DIR


# create ingestion pipeline
def build_pipeline():
    pipeline = IngestionPipeline(
        transformations=[
            SentenceSplitter(chunk_size=500, chunk_overlap=50, paragraph_separator ="\n\n"),
            TitleExtractor(),
            load_local_embedding(),
        ],
        vector_store = get_vector_database(),
        docstore= SimpleDocumentStore(),
    )
    pipeline.persist(PIPELINE_DIR)
    pipeline.load(PIPELINE_DIR)

    return pipeline


# indexing
def create_index(vector_store, embed_model):
    index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        embed_model=embed_model,
    )
    return index