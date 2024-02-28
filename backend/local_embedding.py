"""
default embedding: openAI embedding
this module enables local embedding
"""
from llama_index.embeddings.instructor import InstructorEmbedding
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings

from paths import CACHE_DIR


# loading embed model
def load_local_embedding():
    embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5", cache_folder=CACHE_DIR) 
    return embed_model
