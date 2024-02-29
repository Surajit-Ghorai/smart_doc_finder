"""
ingestion pipeline: processing the input data
"""

import os
import openai
import re
from dotenv import load_dotenv
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import TextNode
from llama_index.core import VectorStoreIndex
from local_llm_model import load_local_llm

from vector_store import get_vector_database
from paths import PIPELINE_DIR, CACHE_DIR, PERSIST_DIR

# loading api key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


# my title extractor
def extract_title(text):

    llm = load_local_llm()
    title = ""
    try:
        title = llm.complete(
            f"Give me a suitable title for the following paragraph: {text}"
        )
        title = title.text
    except Exception as e:
        print(e)
        title = "no title"
    return title


# text splitter
text_parser = SentenceSplitter(
    chunk_size=512, chunk_overlap=64, paragraph_separator="\n\n"
)


# split manually
def split_paragraphs_manually(texts):
    # paragraphs = re.split(r"\n\s*(\r?\n|$)", texts)
    paragraph_regex = r"(?<!\n)\s*(\r?\n){2,}\s*(?!\n)"
    paragraphs = re.split(paragraph_regex, texts)
    paragraphs = [paragraph for paragraph in paragraphs if paragraph.strip()]
    return paragraphs


# splitting into chunks
def split_chunks(doc):
    metadata = doc.metadata
    text_chunks = []
    cur_text_chunks = []
    if (
        metadata["mime type"] == "text/plain"
        or metadata["mime type"] == "application/pdf"
        or metadata["mime type"] == "application/vnd.google-apps.document"
    ):
        cur_text_chunks = split_paragraphs_manually(doc.text)
    else:
        cur_text_chunks = text_parser.split_text(doc.text)

    para_no = 1
    for chunk in cur_text_chunks:
        chunk_metadata = doc.metadata.copy()
        title = extract_title(chunk)
        chunk_metadata["paragraph_number"] = para_no
        chunk_metadata["title"] = title
        text_chunks.append({"text": chunk, "metadata": chunk_metadata})
        print(f"para {para_no} done..")
        para_no += 1

    print("doc done!!!")
    return text_chunks


# converting chunks into nodes
def chunks_to_nodes(splitted_chunks):
    text = splitted_chunks["text"]
    metadata = splitted_chunks["metadata"]
    node = TextNode(
        text=text,
    )
    node.metadata = metadata
    return node


# store in vector_database
def store_in_vector_database(nodes):
    vector_store = get_vector_database()
    vector_store.add(nodes)


# indexing
def create_index(vector_store, embed_model):
    index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        embed_model=embed_model,
    )
    return index
