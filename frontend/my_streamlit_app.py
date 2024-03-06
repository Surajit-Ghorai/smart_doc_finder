"""my streamlit app"""

import os.path
import sys
import streamlit as st
import requests

# importing main module from backend
backend_dir = os.path.abspath("./authentication")
sys.path.insert(1, backend_dir)
import main
auth_dir = os.path.abspath("./authentication")
sys.path.insert(3, auth_dir)
import my_api


def run_app():
    """the streamlit application part"""
    main.process_documents()
    # title of the application
    st.title("Intelligent Document Finder")

    # sidebar
    with st.sidebar:
        st.title("About the app")
        text = """This is a smart document finder app.
        Enter your query and a llm model will give you responses
        from the documents stored in your drive folder."""
        st.markdown(
            f"<div style='white-space: wrap;'>{text}</div>", unsafe_allow_html=True
        )

    # text input field for the user question
    user_question = st.text_input(
        "Enter your query",
        placeholder="Enter your question here...",
    )

    if not user_question:
        st.info("Please add your question to continue.")

    bot_response = []
    # getting the answer from backend parts
    if user_question:
        register_api_url = f"http://127.0.0.1:8000/getanswer/{user_question}"
        response = requests.get(register_api_url)
        print(response)
        print(response.text)
        bot_response, metadata = (
            response.json()["bot_response"],
            response.json()["metadata"],
        )

    with st.container(border=True):
        if bot_response is None or bot_response == []:
            st.write("## Answer")
            st.write("your answer will be displayed here!!")
        else:
            st.write("## Answer")
            st.write(bot_response)
            st.write("### Additional information")
            if metadata is None:
                st.write("No metadata found!!")
            else:
                st.write(f"File name: {metadata['file name']}")
                if "page_label" in metadata:
                    st.write(f"Page number: {metadata['page_label']}")
                else:
                    st.write("Page number: 1")
                st.write(f"Paragraph number: {metadata['paragraph_number']}")
                st.write(f"Tile: {metadata['title']}")
                st.write(f"Author of the file: {metadata['author']}")
