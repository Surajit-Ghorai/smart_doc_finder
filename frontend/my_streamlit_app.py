"""my streamlit app"""

import os.path
import sys
import streamlit as st

# importing main module from backend
backend_dir = os.path.abspath("./backend")
sys.path.insert(1, backend_dir)
import main


def run_app():
    """the streamlit application part"""
    # title of the application
    st.title("Intelligent Document Finder")

    # sidebar
    with st.sidebar:
        st.title("About the app")
        text = "This is a smart document finder app. Enter your query and a llm model will give you response from the documents stored in your drive folder."
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
        bot_response, metadata = main.get_answer(user_question)

    with st.container(border=True):
        if bot_response == None or bot_response == []:
            st.write("## Answer")
            st.write("your answer will be displayed here!!")
        else:
            st.write("## Answer")
            st.write(bot_response)
            st.write("### Additional information")
            st.write(f"File name: {metadata['file name']}")
            if "page_label" in metadata:
                st.write(f"Page number: {metadata['page_label']}")
            else:
                st.write(f"Page number: 1")
            st.write(f"Paragraph number: {metadata['paragraph_number']}")
            st.write(f"Tile: {metadata['title']}")
            st.write(f"Author of the file: {metadata['author']}")
