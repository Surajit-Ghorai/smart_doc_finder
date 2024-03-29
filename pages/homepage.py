"""my homepage app"""

import os
import sys
import re
import streamlit as st
import requests
from time import sleep
from st_pages import Page, hide_pages

backend_dir = os.path.abspath("./backend")
sys.path.insert(2, backend_dir)
import main

def retrieve_folder_id(folder_url):
    """retrieves folder id from url"""
    folder_id = re.search(r"folders/([^/?]+)", folder_url)
    if folder_id:
        return folder_id.group(1)
    else:
        return folder_url

def authenticate_onedrive():
    api_url = f"http://127.0.0.1:8000/authenticate-onedrive"
    access_token = st.session_state["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(api_url, headers= headers)
    st.session_state["onedrive"]=True


def authenticate_googledrive():
    api_url = f"http://127.0.0.1:8000/authenticate-googledrive"
    access_token = st.session_state["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(api_url, headers=headers)
    st.session_state["googledrive"] = True


def homepage():
    """the streamlit application part"""
    hide_pages([Page("/app.py")])
    logged_in = False
    if "logged_in" in st.session_state:
        logged_in = st.session_state["logged_in"]
    else:
        st.session_state["logged_in"] = False

    if st.session_state["logged_in"]:
        # show_pages([Page("pages/logout.py")])

        # title of the application
        st.title("Intelligent Document Finder")

        # sidebar
        with st.sidebar:
            st.title("About the app")
            text = """This is a smart document finder app.
            Enter your query and a llm model will give you responses
            from the documents stored in your drive folder.
            first authenticate your drives:
            """
            st.markdown(
                f"<div style='white-space: wrap;'>{text}</div>", unsafe_allow_html=True
            )

            if st.button("authenticate and load onedrive"):
                authenticate_onedrive()
            if st.button("authenticate and load googledrive"):
                authenticate_googledrive()

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
            # print(st.session_state)
            if "onedrive" not in st.session_state or "googledrive" not in st.session_state:
                st.error("please authenticate onedrive or googledrive")
            elif st.session_state["onedrive"] or st.session_state["googledrive"]:
                folder_id = "my_collection"
                register_api_url = f"http://127.0.0.1:8000/getanswer/{folder_id}/{user_question}"
                access_token = st.session_state["access_token"]
                headers = {"Authorization": f"Bearer {access_token}"}
                response = requests.get(register_api_url, headers= headers)

                print(response.text)
                if response.status_code==200:
                    bot_response, metadata = (
                        response.json()["bot_response"],
                        response.json()["metadata"],
                    )
                else:
                    st.error("not authenticated")
            else:
                st.error("authenticate drive first")

        with st.container(border=True):
            if bot_response is None or bot_response == []:
                st.write("## Answer")
                st.write("your answer will be displayed here!!")
            else:
                st.write("## Answer")
                if bot_response is None:
                    st.write("No answer found!!")
                else:
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
                    st.write(f"Drive: {metadata['drive_type']}")
                    st.write(f"Author of the file: {metadata['author']}")
    else:
        st.error("Log in first!!!")
        with st.spinner('loading the login page...'):
            sleep(2)
        st.switch_page("pages/login_page.py")

homepage()
