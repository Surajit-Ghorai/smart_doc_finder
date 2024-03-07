"""logout page"""

import streamlit as st
import requests
from time import sleep
from st_pages import Page, hide_pages

def check_logout():
    if "logged_in" not in st.session_state:
        st.error("already logged out!!")
        with st.spinner("loading the login page..."):
            sleep(2)
        st.switch_page("pages/login_page.py")
    elif st.session_state["logged_in"]:
        logout()
    else:
        st.error("already logged out!!")
        with st.spinner("loading the login page..."):
            sleep(2)
        st.switch_page("pages/login_page.py")

def logout():
    """logout"""
    hide_pages([Page("/app.py")])

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

    logout_api_url = f"http://127.0.0.1:8000/logout"
    access_token = st.session_state["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.post(logout_api_url, headers= headers)

    if response.status_code==200:
        st.session_state["logged_in"] = False
        st.session_state["access_token"] = None
        st.success("Logged out successfully!!")
        with st.spinner("loading the login page..."):
            sleep(2)
        st.switch_page("pages/login_page.py")
    else:
        st.error("error in logout!!")


check_logout()
