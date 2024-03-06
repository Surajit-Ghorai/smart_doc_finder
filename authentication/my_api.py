"""register"""
import os
import uvicorn
import schemas
import models
import jwt
from dotenv import load_dotenv
from datetime import datetime
from models import User, TokenTable
from database import Base, engine, SessionLocal
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from auth_bearer import JWTBearer
from functools import wraps
from utils import (
    create_access_token,
    create_refresh_token,
    verify_password,
    get_hashed_password,
)
from auth_bearer import JWTBearer
import os.path
import sys
import streamlit as st

# importing main module from backend
backend_dir = os.path.abspath("./backend")
sys.path.insert(1, backend_dir)
import main

# env variables
load_dotenv()
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES"))
ALGORITHM = os.getenv("ALGORITHM")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY")


Base.metadata.create_all(engine)


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


app = FastAPI()


@app.post("/register")
def register_user(user: schemas.User, session: Session = Depends(get_session)):
    existing_user = session.query(models.User).filter_by(email=user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    encrypted_password = get_hashed_password(user.password)

    new_user = models.User(
        username=user.username, email=user.email, password=encrypted_password
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return {"message": "user created successfully"}


@app.post("/login", response_model=schemas.TokenSchema)
def login(request: schemas.requestdetails, db: Session = Depends(get_session)):
    print("inside login api")
    user = db.query(User).filter(User.email == request.email).first()
    print(f"{user.username}, {user.password}")
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email"
        )
    hashed_pass = user.password
    if not verify_password(request.password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect password"
        )

    access = create_access_token(user.user_id)
    refresh = create_refresh_token(user.user_id)
    print(access, refresh)
    token_db = models.TokenTable(
        user_id=user.user_id, access_token=access, refresh_token=refresh, status=True
    )
    db.add(token_db)
    db.commit()
    db.refresh(token_db)
    return {
        "access_token": access,
        "refresh_token": refresh,
    }


@app.get("/getusers")
def getusers(
    dependencies=Depends(JWTBearer()), session: Session = Depends(get_session)
):
    user = session.query(models.User).all()
    return user


@app.post("/change-password")
def change_password(
    request: schemas.changepassword, db: Session = Depends(get_session)
):
    user = db.query(models.User).filter(models.User.email == request.email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User not found"
        )

    if not verify_password(request.old_password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid old password"
        )

    encrypted_password = get_hashed_password(request.new_password)
    user.password = encrypted_password
    db.commit()

    return {"message": "Password changed successfully"}


@app.post("/logout")
def logout(dependencies=Depends(JWTBearer()), db: Session = Depends(get_session)):
    token = dependencies
    payload = jwt.decode(token, JWT_SECRET_KEY, ALGORITHM)
    user_id = payload["sub"]
    token_record = db.query(models.TokenTable).all()
    info = []
    for record in token_record:
        print("record", record)
        if (datetime.now() - record.created_date).days > 1:
            info.append(record.user_id)
    if info:
        existing_token = (
            db.query(models.TokenTable).where(TokenTable.user_id.in_(info)).delete()
        )
        db.commit()

    existing_token = (
        db.query(models.TokenTable)
        .filter(
            models.TokenTable.user_id == user_id, models.TokenTable.access_token == token
        )
        .first()
    )
    if existing_token:
        existing_token.status = False
        db.add(existing_token)
        db.commit()
        db.refresh(existing_token)
    return {"message": "Logout Successfully"}


@app.get("/getanswer/{question}")
def getanswer(
    question: str,
    dependencies=Depends(JWTBearer()), session: Session = Depends(get_session)
):
    bot_response, metadata = main.get_answer(question)
    return {"user_question": question, "bot_response":bot_response, "metadata":metadata}


def token_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):

        payload = jwt.decode(kwargs["dependencies"], JWT_SECRET_KEY, ALGORITHM)
        user_id = payload["sub"]
        data = (
            kwargs["session"]
            .query(models.TokenTable)
            .filter_by(user_id=user_id, access_token=kwargs["dependencies"], status=True)
            .first()
        )
        if data:
            return func(kwargs["dependencies"], kwargs["session"])

        else:
            return {"msg": "Token blocked"}

    return wrapper

if __name__ == "__main__":
    uvicorn.run("my_api:app", host="127.0.0.1", port=8000, reload=True)
