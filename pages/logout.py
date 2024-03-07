"""logout page"""

import streamlit as st
import requests
from time import sleep
from st_pages import Page, show_pages

def logout():
    """logout"""
    if st.session_state["logged_in"]:
        #show_pages([Page("pages/signup.py"), Page("pages/login_page.py")])

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
        st.session_state["logged_in"] = False
        st.success("Logged out successfully!!")
        with st.spinner("loading the login page..."):
            sleep(2)
        st.switch_page("pages/login_page.py")

    else:
        st.error("You are already logged out!!!")
        with st.spinner("loading the login page..."):
            sleep(2)
        st.switch_page("pages/login_page.py")


logout()
