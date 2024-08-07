import logging
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError

from src.config import settings
from src.models import DefaultResponseMessage, TokenPayload, Device


reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/access-token")
TokenDep = Annotated[str, Depends(reusable_oauth2)]


def validate_token(token: TokenDep) -> Device | None:
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
    return Device(device_id=token_data.sub)


CurrentDev = Annotated[Device, Depends(validate_token)]

responses_403 = {"description": "Forbidden", "model": DefaultResponseMessage}
responses_422 = {"description": "Not Found", "model": DefaultResponseMessage}
