import logging
from collections.abc import Generator
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session

from src.core import security
from src.core.config import settings
from src.core.db import engine
from src.models import DefaultResponseMessage, TokenPayload, User


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session  # So it can close the session after the request is finished


reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.USERAPI_API_V1_STR}/access-token"
)

SessionDep = Annotated[Session, Depends(get_db)]  # And then MetaData do be injected
TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_current_user(session: SessionDep, token: TokenDep) -> User:
    logger = logging.getLogger("get_current_user")
    logger.info("Getting current user")

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)

    except (InvalidTokenError, ValidationError):
        logger.error("Could not validate credentials")
        raise HTTPException(
            status_code=403,
            detail="Could not validate credentials",
        )

    user = session.get(User, token_data.sub)
    if not user:
        logger.error("User %s not found", token_data.sub)
        raise HTTPException(status_code=404, detail="User not found")

    if not user.is_active:
        logger.error("User %s is inactive", token_data.sub)
        raise HTTPException(status_code=401, detail="Inactive user")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_active_superuser(current_user: CurrentUser) -> User:
    logger = logging.getLogger("get_current_active_superuser")
    logger.info("Getting current active superuser")
    if not current_user.is_superuser:
        logger.error("User %s is not a superuser", current_user.id)
        raise HTTPException(status_code=403, detail="Not enough privileges")
    return current_user


responses_401 = {"description": "Unauthorized", "model": DefaultResponseMessage}
responses_403 = {"description": "Forbidden", "model": DefaultResponseMessage}
responses_404 = {"description": "Not Found", "model": DefaultResponseMessage}
responses_409 = {"description": "Conflict", "model": DefaultResponseMessage}
responses_422 = {"description": "Not Found", "model": DefaultResponseMessage}
