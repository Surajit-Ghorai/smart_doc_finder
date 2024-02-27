"""
customizing query engine
"""

from llama_index.core import get_response_synthesizer
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.postprocessor import SimilarityPostprocessor


def build_query_engine(index):
    """returns a query engine"""
    # configure retriever
    retriever = VectorIndexRetriever(
        index=index,
        similarity_top_k=3,
    )

    # configure response synthesizer
    response_synthesizer = get_response_synthesizer()

    # assemble query engine
    query_engine = RetrieverQueryEngine(
        retriever=retriever,
        response_synthesizer=response_synthesizer,
        node_postprocessors=[SimilarityPostprocessor(similarity_cutoff=0.3)],
    )

    return query_engine
