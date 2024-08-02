import logging
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

import src.api.dependencies as deps
import src.core.security as security
import src.crud as crud
import src.mail.utils as mail
from src.core.config import settings
from src.models import DefaultResponseMessage, NewPassword, Token, User, UserResponse

router = APIRouter()


@router.post("/login/test-token", response_model=UserResponse)
def test_token(current_user: deps.CurrentUser) -> User | HTTPException:
    """
    Test the access token
    """
    logging.getLogger("/login/test-token").info(
        "User %s is testing its own token", current_user.username
    )
    return current_user


@router.post("/access-token", responses={401: deps.responses_401})
async def access_token(
    session: deps.SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    """
    OAuth2 compatible token login | Get an access token for future request using
    **USERNAME**
    **PASSWORD**
    """
    logger = logging.getLogger("/access-token")
    logger.info("User %s is trying to authenticate", form_data.username)

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

    logger.info("User %s authenticated successfully", form_data.username)
    return Token(access_token=token)


@router.post("/password-recovery/{email}")
def recover_password(email: str, session: deps.SessionDep) -> DefaultResponseMessage:
    """
    Password Recovery for any user. By email.
    """
    logger = logging.getLogger("/password-recovery")
    logger.info("User is trying to recover its password")

    user = crud.get_user_by_email(db=session, email=email)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this email does not exist in the system.",
        )

    password_reset_token = security.generate_password_reset_token(email=email)

    email_data = mail.generate_reset_password_email(
        email_to=email, username=user.username, token=password_reset_token
    )
    mail.send_email(
        email_to=email,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )

    logger.info("Password recovery email sent")
    return DefaultResponseMessage(message="Password recovery email sent")


@router.post("/reset-password/")
def reset_password(
    session: deps.SessionDep, body: NewPassword
) -> DefaultResponseMessage:
    """
    Reset password. Requires the reset token sent by email and the new password.
    """
    logger = logging.getLogger("/reset-password")
    logger.info("User is trying to reset its password")

    token_decoded_email = security.verify_password_reset_token(token=body.token)
    if not token_decoded_email:
        raise HTTPException(status_code=400, detail="Invalid token")

    user = crud.get_user_by_email(db=session, email=token_decoded_email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this email does not exist in the system.",
        )
    elif not user.is_active:
        raise HTTPException(status_code=401, detail="Inactive user")

    crud.update_password(db=session, user=user, new_password=body.new_password)

    logger.info("Password updated successfully")
    return DefaultResponseMessage(message="Password updated successfully")
