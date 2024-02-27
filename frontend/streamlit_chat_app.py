'''my streamlit chat app'''
import streamlit as st

def find_answer():
    return "backend not available!!"

with st.sidebar:
    menu = st.title("My Menu")
    option1 = st.button("home")
    option2 = st.button("profile")
    option3 = st.button("about me")
    option4 = st.button("exit")

st.title("Intelligent Document Finder")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Enter your question/query here"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    response = f"Answer: {prompt}"
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
