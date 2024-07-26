from typing import Any
from datetime import datetime, timedelta

import jwt
from passlib.context import CryptContext

from src.core.config import settings


ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")


def get_password_hash(paswd: str) -> str:
    return pwd_context.hash(paswd)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    expire = datetime.now() + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt =  jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
