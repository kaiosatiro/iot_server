import logging
from typing import Annotated
from datetime import datetime, timedelta
from typing import Any

import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import ValidationError

from src.config import settings
from src.models import DefaultResponseMessage, TokenPayload


reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/access-token")
TokenDep = Annotated[str, Depends(reusable_oauth2)]


def create_device_access_token(device_id: int | Any) -> str:
    to_encode = {"sub": str(device_id)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def validate_token(token: TokenDep) -> TokenPayload | None:
    logger = logging.getLogger("validate_token")
    logger.info("Validating token")

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)

    except (InvalidTokenError, ValidationError):
        logger.error("Invalid token: %s", token)
        raise HTTPException(
            status_code=403,
            detail="Could not validate credentials",
        )
    logger.info("Token validated")
    return token_data


CurrentDev = Annotated[TokenPayload, Depends(validate_token)]

responses_403 = {"description": "Forbidden", "model": DefaultResponseMessage}
responses_422 = {"description": "Not Found", "model": DefaultResponseMessage}
