"""varifies authentication for jwt headers"""
import jwt
import os
from dotenv import load_dotenv
from jwt.exceptions import InvalidTokenError
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models import TokenTable
from utils import (
    create_access_token,
    create_refresh_token,
)

# env variables
load_dotenv()
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_MINUTES = 7*24*30
ALGORITHM = "HS256"
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY")


def decodeJWT(jwtoken: str):
    try:
        # Decode and verify the token
        payload = jwt.decode(jwtoken, JWT_SECRET_KEY, ALGORITHM)
        return payload
    except InvalidTokenError:
        return None


def verify_jwt(jwtoken: str) -> bool:
    isTokenValid: bool = False

    try:
        payload = decodeJWT(jwtoken)
        if payload:
            isTokenValid = True
    except jwt.ExpiredSignatureError:
        # Token has expired, attempt to refresh
        payload = None
        if refresh_token := get_refresh_token_from_payload(jwtoken):
            new_access_token = refresh_access_token(refresh_token)
            if new_access_token:
                is_token_valid = True
    except InvalidTokenError:
        payload = None

    return isTokenValid


def refresh_access_token(refresh_token: str) -> str:
    try:
        payload = jwt.decode(
            refresh_token, JWT_REFRESH_SECRET_KEY, ALGORITHM
        )
        user_id = payload.get(
            "user_id"
        ) 
        if user_id:
            new_access_token = create_access_token(user_id)
            return new_access_token
    except InvalidTokenError:
        return None


def get_refresh_token_from_payload(jwtoken: str) -> str:
    try:
        payload = jwt.decode(jwtoken, JWT_SECRET_KEY, ALGORITHM)
        refresh_token = payload.get("refresh_token")
        return refresh_token
    except InvalidTokenError:
        return None


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(
            JWTBearer, self
        ).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=403, detail="Invalid authentication scheme."
                )
            if not verify_jwt(credentials.credentials):
                raise HTTPException(
                    status_code=403, detail="Invalid token or expired token."
                )
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")


jwt_bearer = JWTBearer()
