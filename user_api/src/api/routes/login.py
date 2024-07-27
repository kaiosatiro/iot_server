import logging
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

import src.api.dependencies as deps
import src.core.security as security
import src.crud as crud
from src.core.config import settings
from src.models import Token

router = APIRouter()


@router.post("/access-token")
async def login_access_token(
    session: deps.SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    logger = logging.getLogger("/access-token")

    user = crud.authenticate_user(
        db=session, username=form_data.username, password=form_data.password
    )

    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    elif not user.is_active:
        raise HTTPException(status_code=401, detail="Inactive user")

    token = security.create_access_token(
        subject=user.id,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return Token(access_token=token)
