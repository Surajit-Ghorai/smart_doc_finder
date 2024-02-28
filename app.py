"""entrypoint to the application connecting both frontend and backend"""
from frontend import my_streamlit_app

def app():
    """this method runs the application"""
    my_streamlit_app.run_app()

if __name__ == "__main__":
    app()
