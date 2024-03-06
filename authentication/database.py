"""my postgresql database"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
# from sqlalchemy.ext.declarative import declarative_base

# load env variables
load_dotenv()
user = os.getenv("postgresql_user")
password = os.getenv("postgresql_password")


# main part
Base = declarative_base()
db_url = f"postgresql://{user}:{password}@localhost/llama_app"
engine = create_engine(db_url, echo=True)
SessionLocal = sessionmaker(
    bind=engine, expire_on_commit=False
)
