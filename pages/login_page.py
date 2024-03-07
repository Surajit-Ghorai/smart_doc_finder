"""login page"""

import streamlit as st
import requests
from time import sleep
from st_pages import Page, hide_pages

def check_login():
    if "logged_in" not in st.session_state:
        login_app()
    elif st.session_state["logged_in"]:
        st.error("already logged in, log out first")
    else:
        login_app()

def login_app():
    """log in page"""
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

    st.text("welcome to the application")
    st.text("Please login first")

    with st.form("login form"):
        email = st.text_input(
            label="Email",
            max_chars=50,
            placeholder="example@gmail.com",
            help="enter your email address",
        )
        password = st.text_input(
            label="Password",
            type="password",
            max_chars=50,
            placeholder="password",
            help="Enter your password",
        )
        login_button = st.form_submit_button(label="Login")
        if login_button:
            if email and password:
                login_api_url = "http://127.0.0.1:8000/login"
                login_data = {
                    "email": email,
                    "password": password,
                }
                response = requests.post(login_api_url, json=login_data)
                # print(response)
                if response.status_code == 200:
                    print("logged in successfully...")
                    st.success("logged in successfully!!")
                    st.toast("logged in successfully!!", icon="🥂")

                    st.session_state["logged_in"] = True
                    st.session_state["access_token"] =response.json()["access_token"]
                    st.session_state["refresh_token"] = response.json()["refresh_token"]

                    with st.spinner("loading the home page..."):
                        sleep(2)
                    st.switch_page("pages/homepage.py")
                else:
                    st.error(f"error: {response.status_code}, {response.text}")
            else:
                st.error("Please enter your email and password")

    st.text("Don't have an account. Register below 👇")
    st.page_link("pages/signup.py", label="sign up")

check_login()
