# **Project Title:** Intelligent Document Finder with Llama Index

**Description:**

This project automates document upload, processing, and search functionality, enabling users to easily find relevant information within uploaded documents.

**Features:**

- **Document Upload:** Upload documents of various formats (.txt, .pdf, .docx, .csv, .pptx etc.) to a designated Google Drive folder.
- **Processing and Indexing:** Automatically transfer documents to a server, process them using Llama Index, and create a searchable database with detailed metadata (titles, paragraph numbers, page numbers, etc.).
- **Search Interface:** Utilize a user-friendly frontend to search the indexed data, retrieving relevant document snippets and comprehensive metadata.

**Video documentation link:** <https://drive.google.com/file/d/1CD2wHhhvycIiTHPCPjNVRjB--tUbI_A9/view?usp=sharing>
**Tech Stack:**

- Python (>= 3.11 and < 3.12)
- Llama Index
- Hugging Face
- Chroma DB
- Streamlit
- Google Drive API
- Google Cloud Console

**Setup Instructions:**

1. **Prerequisites:** Ensure you have a Python version greater than or equal to 3.11, but strictly less than 3.12 installed on your system.
1. **Code Acquisition:** Download the code from the GitHub repository or clone it using your preferred method.
1. **Virtual Environment:** Create a virtual environment using python -m venv your\_venv\_name.
1. **Activate Environment:** Activate the virtual environment:
   1. Windows: .your\_venv\_name\Scripts\activate
   1. Linux / Mac OS: source your\_venv\_name/bin/activate
1. **Install Dependencies:** Install requirements listed in requirements.txt using pip install -r requirements.txt.
1. **Configuration:**
   1. Create a .env folder and store your Google PALM API key there.
   1. Create a Google Cloud Platform (GCP) project, enable the Google Drive API, and create a service account.
   1. Download the service account key file and rename it to credentials.json in the project directory.
   1. In constants.py, update the FOLDER\_ID variable with the ID of the Google Drive folder where documents are stored.

**Usage Instructions:**

1. Go to the project directory.
1. Open your terminal.
1. Run the application using streamlit run app.py.
1. The Streamlit app will launch in your web browser, but might take some time to load initially (especially during the first run).
1. Enter your search query in the user interface.
1. The app will retrieve and display relevant document snippets with detailed metadata matching your search.

**System architecture:**

<img width="4400" alt="project structure" src="https://github.com/Surajit-Ghorai/smart_doc_finder/assets/158047469/e00891ff-819e-4526-9f22-2dde9622325e">

Here is the flowchart diagram link : <https://www.figma.com/file/2StIULgYp7UaCGtsLRKPnY/project-structure?type=whiteboard&node-id=603%3A139&t=pGdBAtzKeHVS0IPe-1>

**Process Details:**

Here's a detailed breakdown of the application's workflow:

1. **Document Loading:**
   1. Upon application start, the system utilizes GoogleDriveReader from the Llama Hub to load documents from the designated Google Drive folder.
   1. To identify new documents, the application:
      1. Extracts file IDs from both the loaded documents and the existing documents stored in the Chroma vector database.
      1. Compares these sets to identify any new file IDs, indicating newly uploaded documents.
1. **Processing:**
   1. For newly identified documents:
      1. Documents are split into smaller chunks for efficient processing. This is done manually for specific formats (TXT, PDF, DOCX) and using Llama Index's SentenceSplitter for others.
      1. Titles and paragraph numbers are extracted for each chunk and added to the metadata.
      1. Text chunks are converted into TextNode objects and then embedded using the BAAI/bge-small-en-v1.5 model from Hugging Face.
   1. The processed data (embeddings and metadata) is then stored in the ChromaDB vector store.
1. **Search and Retrieval:**
   1. When a user submits a search query:
      1. Documents are retrieved from ChromaDB and indexed.
      1. The indexed data is passed to the query machine.
      1. The query machine retrieves relevant contexts from the vector store using the LLM model, gemini-pro.
      1. Finally, we get our answer along with metadata.

**Resources used:**

To support my learning and project development, I leveraged various resources, including:

- The official Llama Index documentation : <https://docs.llamaindex.ai/en/stable/>, <https://docs.llamaindex.ai/en/stable/examples/ingestion/ingestion_gdrive.html>, <https://docs.llamaindex.ai/en/stable/examples/low_level/ingestion.html#build-an-ingestion-pipeline-from-scratch> etc.
- A guide on using Google Drive with ChatGPT :<https://betterprogramming.pub/using-google-drive-as-a-knowledge-base-for-your-chatgpt-application-805962812547>
- A comprehensive guide to LlamaIndex on Medium : <https://medium.com/@rishik58/harnessing-the-power-of-llamaindex-a-comprehensive-guide-to-next-generation-data-handling-919313a4e822>
- Documentation for Google Drive API : <https://developers.google.com/drive>
- Streamlit documentation: <https://docs.streamlit.io/>
