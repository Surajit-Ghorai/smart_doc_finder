'''my streamlit app'''
import sys
sys.path.append(r'C:\Users\promact\new_project_task\Intelligent_document_finder\trial')

import streamlit as st
import basic

def find_answer():
    return "backend not available!!"

st.title("Intelligent Document Finder")

user_question = st.text_input(
    "Enter your query",
    placeholder="Enter your question here...",
)

#user_question = st.chat_input("Enter your query")

if not user_question:
    st.info("Please add your question to continue.")

bot_response = []
if user_question:
    bot_response = basic.get_answer(user_question)

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
