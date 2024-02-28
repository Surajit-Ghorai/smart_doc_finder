'''my streamlit app'''
import os.path
import sys
import streamlit as st

# importing main module from backend 
backend_dir = os.path.abspath("./backend")
sys.path.insert(1, backend_dir)
import main

def run_app():
    st.title("Intelligent Document Finder")

    user_question = st.text_input(
        "Enter your query",
        placeholder="Enter your question here...",
    )

    if not user_question:
        st.info("Please add your question to continue.")

    bot_response = []
    if user_question:
        bot_response = main.get_answer(user_question)

    with st.container(border=True):
        if bot_response == None or bot_response == []:
            st.write("## Answer")
            st.write("your answer will be displayed here!!")
        else:
            st.write("## Answer")
            st.write(bot_response[0])
            st.write("### Source")
            st.write(f"File name: {bot_response[1]}")
            st.write(f"Page number: {bot_response[2]}")
            #st.write(f"file location: {answer.source_nodes[0].metadata['file id']}")
