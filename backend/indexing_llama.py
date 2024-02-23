'''for testing indexing of files from drive automatically'''
import os
import openai
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

load_dotenv()

google_api_key = os.getenv("GOOGLE_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")

openai.api_key = openai_api_key

# testing llamaindex working or not
documents = SimpleDirectoryReader(input_files=[r"C:\Users\promact\Downloads\bear_story.pdf"]).load_data()
index = VectorStoreIndex.from_documents(documents)

query_engine = index.as_query_engine()
response = query_engine.query("what the bear said")
print(response)
