import logging
import re

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import func, select

import src.api.dependencies as deps
from src import crud
from src.core.config import settings
from src.core.security import verify_password
from src.mail.utils import generate_new_account_email, send_email
from src.models import (
    DefaultResponseMessage,
    UpdatePassword,
    User,
    UserCreation,
    UserResponse,
    UsersListResponse,
    UserUpdate,
    UserUpdateMe,
)

router = APIRouter()


@router.get(
    "/me",
    tags=["Users"],
    response_model=UserResponse,
    responses={401: deps.responses_401, 403: deps.responses_403},
)
async def read_me(*, current_user: deps.CurrentUser) -> User | HTTPException:
    """
    Get current user.
    """
    logger = logging.getLogger("users/me")
    logger.info("User %s is reading its own information", current_user.username)
    return current_user


@router.patch(
    "/me",
    tags=["Users"],
    response_model=UserResponse,
    responses={
        401: deps.responses_401,
        403: deps.responses_403,
        409: deps.responses_409,
    },
)
def update_me(
    *, session: deps.SessionDep, user_in: UserUpdateMe, current_user: deps.CurrentUser
) -> User | HTTPException:
    """
    Update own user.
    """
    logger = logging.getLogger("PATCH users/me")
    logger.info("User %s is updating its own information", current_user.username)

    if user_in.email:
        existing_user = crud.get_user_by_email(db=session, email=user_in.email)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=409, detail="User with this email already exists"
            )
    if user_in.username:
        existing_user = crud.get_user_by_username(db=session, username=user_in.username)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=409, detail="User with this username already exists"
            )

    current_user = crud.update_user(
        db=session, db_user=current_user, user_new_input=user_in
    )

    logger.info("User %s updated successfully", current_user.username)
    return current_user


@router.patch(
    "/me/password",
    tags=["Users"],
    response_model=DefaultResponseMessage,
    responses={
        401: deps.responses_401,
        403: deps.responses_403,
        409: deps.responses_409,
    },
)
def update_my_password(
    *, session: deps.SessionDep, body: UpdatePassword, current_user: deps.CurrentUser
) -> DefaultResponseMessage | HTTPException:
    """
    Update own password.
    """
    logger = logging.getLogger("PATCH users/me/password")
    logger.info("User %s is updating its own password", current_user.username)

    if not verify_password(body.current_password, current_user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect password")

    if body.current_password == body.new_password:
        raise HTTPException(
            status_code=409, detail="New password cannot be the same as the current one"
        )

    crud.update_password(db=session, user=current_user, new_password=body.new_password)

    logger.info("Password updated successfully")
    return DefaultResponseMessage(message="Password updated successfully")


@router.delete(
    "/me",
    tags=["Users"],
    response_model=DefaultResponseMessage,
    responses={401: deps.responses_401, 403: deps.responses_403},
)
async def deactivate_me(
    session: deps.SessionDep, current_user: deps.CurrentUser
) -> DefaultResponseMessage | HTTPException:
    """
    Deactivate own user.
    """
    logger = logging.getLogger("DELETE users/me")
    logger.info("User %s is deactivating itself", current_user.username)

    if current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )
    crud.deactivate_user(db=session, user=current_user)

    logger.info("User %s deactivated successfully", current_user.username)
    return DefaultResponseMessage(message="User deactivated successfully")


@router.get(
    "/",
    tags=["Admin"],
    dependencies=[Depends(deps.get_current_active_superuser)],
    response_model=UsersListResponse,
)
async def read_users(*, session: deps.SessionDep) -> UsersListResponse | HTTPException:
    """
    Retrieve users.
    """
    logger = logging.getLogger("GET users/")
    logger.info("Admin is retrieving all users")

    count_statement = select(func.count()).select_from(User)
    count = session.exec(count_statement).one()

    statement = select(User)
    users = session.exec(statement).all()

    logger.info("Returning %s users", count)
    return UsersListResponse(data=users, count=count)


@router.get(
    "/{user_id}",
    tags=["Admin"],
    dependencies=[Depends(deps.get_current_active_superuser)],
    response_model=UserResponse,
)
async def read_user_by_id(
    *, user_id: int, session: deps.SessionDep
) -> User | HTTPException:
    """
    Get a specific user by id.
    """
    logger = logging.getLogger("GET users/{id}")
    logger.info("Admin is retrieving user %s", user_id)

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    logger.info("Returning user %s", user_id)
    return user


@router.post(
    "/",
    tags=["Admin"],
    dependencies=[Depends(deps.get_current_active_superuser)],
    response_model=UserResponse,
    status_code=201,
)
async def create_user(
    *, session: deps.SessionDep, user_in: UserCreation
) -> User | HTTPException:
    """
    Create new user. The **name**, **email** and **password** are required. An email is sent.
    """
    logger = logging.getLogger("POST users/")
    logger.info("Admin is creating a new user")

    user = crud.get_user_by_email(db=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=409,
            detail="The user with this email already exists in the system.",
        )
    user = crud.get_user_by_username(db=session, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=409,
            detail="The user with this username already exists in the system.",
        )

    user = crud.create_user(db=session, user_input=user_in)
    if settings.emails_enabled and user_in.email:
        email_data = generate_new_account_email(
            email_to=user_in.email, username=user_in.email, password=user_in.password
        )
        send_email(
            email_to=user_in.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )

    logger.info("User %s created successfully", user.id)
    return user


@router.patch(
    "/{id}",
    tags=["Admin"],
    dependencies=[Depends(deps.get_current_active_superuser)],
    response_model=UserResponse,
)
async def update_user(
    *, id: int, session: deps.SessionDep, user_in: UserUpdate
) -> User | HTTPException:
    """
    Update some user.
    """
    logger = logging.getLogger("PATCH users/{id}")
    logger.info("Admin is updating user %s", id)

    user = session.get(User, id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        user = crud.update_user(db=session, db_user=user, user_new_input=user_in)

    except IntegrityError as e:
        match = re.search(r"Key \((.*?)\)", str(e.orig))
        if match:
            key_info = match.group(1)
            logger.error(e.orig)
        else:
            logger.error("IntegrityError occurred, but no key information found.")

        raise HTTPException(
            status_code=409, detail=f"This {key_info} already exists in the system."
        )

    logger.info("User %s updated successfully", id)
    return user


@router.delete(
    "/{id}",
    tags=["Admin"],
    dependencies=[Depends(deps.get_current_active_superuser)],
    response_model=DefaultResponseMessage,
)
async def delete_user(
    *, id: int, session: deps.SessionDep, current_user: deps.CurrentUser
) -> DefaultResponseMessage | HTTPException:
    """
    Deactivate some user.
    """
    logger = logging.getLogger("DELETE users/{id}")
    logger.info("Admin is deactivating user %s", id)

    user = session.get(User, id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.is_active:
        raise HTTPException(status_code=404, detail="User already deactivated")

    if user == current_user:
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )

    crud.deactivate_user(db=session, user=user)

    logger.info("User %s deactivated successfully", id)
    return DefaultResponseMessage(message="User deactivated successfully")
