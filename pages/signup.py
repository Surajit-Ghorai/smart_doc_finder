"""sign up page"""

import streamlit as st
import requests
from time import sleep
from st_pages import Page, hide_pages


def signup_app():
    """sign up page"""
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
    st.text("Please register your details before login")

    with st.form("signup form"):
        username = st.text_input(
            label="User name",
            max_chars=50,
            placeholder="username",
            help="enter your name",
        )
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
        signup_button = st.form_submit_button("Register")
        if signup_button:
            if username and email and password:
                register_api_url = "http://127.0.0.1:8000/register"
                request_data = {
                    "username": username,
                    "email": email,
                    "password": password,
                }
                response = requests.post(register_api_url, json=request_data)
                print(response)
                print(response.text)
                if response.status_code == 200:
                    st.success("registered successfully!!")
                    st.toast("registered successfully!!", icon="🥂")
                    with st.spinner('loading the home page...'):
                        login_api_url = "http://127.0.0.1:8000/login"
                        login_data = {
                            "email": email,
                            "password": password,
                        }
                        response = requests.post(login_api_url, json=login_data)

                        if response.status_code == 200:
                            print("logged in successfully...")
                            st.session_state["logged_in"] = True
                            st.session_state["access_token"] =response.json()["access_token"]
                            st.session_state["refresh_token"] = response.json()["refresh_token"]
                        else:
                            st.error("there was some issue in automatic login, goto login page")

                        sleep(1)
                    st.switch_page("pages/homepage.py")
                else:
                    st.error(f"error: {response.status_code}, {response.text}")
            else:
                st.error("Please fill all the fields")

    st.write("Already have an account? Login below 👇")
    st.page_link("pages/login_page.py", label="Login")

signup_app()
