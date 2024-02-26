'''my streamlit app'''
import streamlit as st

with st.sidebar:
    menu = st.text_input("My Menu")

st.title("Intelligent Document Finder")

uploaded_file = st.file_uploader("Upload any document")

question = st.text_input(
    "Ask something about the article",
    placeholder="Can you give me a short summary?",
    disabled=not uploaded_file,
)

if uploaded_file and not question:
    st.info("Please add your question to continue.")

if uploaded_file and question:
    article = uploaded_file.read().decode()

    st.write("### Answer")
    st.write("here is an answer")
