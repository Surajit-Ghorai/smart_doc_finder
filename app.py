"""application"""

import streamlit as st
from st_pages import Page, show_pages
from pages import login_page, signup, homepage
from time import sleep


if __name__ == "__main__":
    #print("session state: ", st.session_state)
    # show_pages([Page("pages/signup.py"), Page("pages/login_page.py")])
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
        login_page.login_app()
    elif st.session_state["logged_in"] == False:
        login_page.login_app()
    else:
        homepage.homepage()
