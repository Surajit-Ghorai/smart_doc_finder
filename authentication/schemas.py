"""schemas"""
from pydantic import BaseModel
from typing import Optional
import datetime

class User(BaseModel):
    username: str
    email: str
    password: str


class requestdetails(BaseModel):
    email: str
    password: str


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str


class changepassword(BaseModel):
    email: str
    old_password: str
    new_password: str


class TokenCreate(BaseModel):
    user_id: str
    access_token: str
    refresh_token: str
    status: bool
    created_date: datetime.datetime

class AnswerSchema(BaseModel):
    user_question: str
    bot_response: Optional[str] = None
    metadata: Optional[dict] = None
