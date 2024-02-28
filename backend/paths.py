"""managing paths"""
import os.path
import sys

# paths
base_path = os.path.abspath(".")

# persist_dir path to store embeddings locally
PERSIST_DIR = base_path + "\persist_dir"

# cache_dir path to store embedding_model locally
CACHE_DIR = base_path + "\cache_dir"

# local pipeline storage
PIPELINE_DIR = base_path + "\local_pipeline_storage"

# constants module path
sys.path.insert(2,base_path)
import constants
