import logging
import re
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import func, select

import src.api.dependencies as deps
from src import crud
from src.core.security import get_password_hash, verify_password
from src.models import (
    DefaultResponseMessage,
    UpdatePassword,
    User,
    UserCreation,
    UserResponseObject,
    UsersListResponse,
    UserUpdate,
    UserUpdateMe,
)

router = APIRouter()


@router.get("/me", tags=["Users"], response_model=UserResponseObject)
async def read_user_me(*, current_user: deps.CurrentUser) -> User | HTTPException:
    """
    Get current user.
    """
    logger = logging.getLogger("users/me")  # use generate custom id?
    return current_user


@router.patch("/me", tags=["Users"], response_model=UserResponseObject)
def update_user_me(
    *, session: deps.SessionDep, user_in: UserUpdateMe, current_user: deps.CurrentUser
) -> Any:
    """
    Update own user.
    """
    logger = logging.getLogger("PATCH users/me")

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
    return current_user


@router.patch("/me/password", tags=["Users"], response_model=DefaultResponseMessage)
def update_password_me(
    *, session: deps.SessionDep, body: UpdatePassword, current_user: deps.CurrentUser
) -> Any:
    """
    Update own password.
    """
    logger = logging.getLogger("PATCH users/me/password")

    logger.debug(body.current_password)
    logger.debug(body.new_password)
    logger.debug(get_password_hash(body.current_password))
    logger.debug(get_password_hash(body.new_password))
    logger.debug(current_user.hashed_password)

    if not verify_password(body.current_password, current_user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect password")

    if body.current_password == body.new_password:
        raise HTTPException(
            status_code=422, detail="New password cannot be the same as the current one"
        )

    if crud.update_password(
        db=session, user=current_user, new_password=body.new_password
    ):
        return DefaultResponseMessage(message="Password updated successfully")


@router.delete("/me", tags=["Users"], response_model=DefaultResponseMessage)
async def dactivate_user_me(
    session: deps.SessionDep, current_user: deps.CurrentUser
) -> Any:
    """
    Deactivate own user.
    """
    if current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )
    crud.deactivate_user(db=session, user=current_user)

    return DefaultResponseMessage(message="User deactivated successfully")


@router.get(
    "/",
    tags=["Admin"],
    dependencies=[Depends(deps.get_current_active_superuser)],
    response_model=UsersListResponse,
)
async def read_users(*, session: deps.SessionDep) -> Any:
    """
    Retrieve users.
    """
    count_statement = select(func.count()).select_from(User)
    count = session.exec(count_statement).one()

    statement = select(User)
    users = session.exec(statement).all()

    return UsersListResponse(data=users, count=count)


@router.get(
    "/{user_id}",
    tags=["Admin"],
    dependencies=[Depends(deps.get_current_active_superuser)],
    response_model=UserResponseObject,
)
async def read_user_by_id(*, user_id: int, session: deps.SessionDep) -> Any:
    """
    Get a specific user by id.
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post(
    "/",
    tags=["Admin"],
    dependencies=[Depends(deps.get_current_active_superuser)],
    response_model=UserResponseObject,
    status_code=201,
)
async def create_user(*, session: deps.SessionDep, user_in: UserCreation) -> Any:
    """
    Create new user.
    """
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
    # if settings.emails_enabled and user_in.email:
    #     email_data = generate_new_account_email(
    #         email_to=user_in.email, username=user_in.email, password=user_in.password
    #     )
    #     send_email(
    #         email_to=user_in.email,
    #         subject=email_data.subject,
    #         html_content=email_data.html_content,
    #     )
    return user


@router.patch(
    "/{id}",
    tags=["Admin"],
    dependencies=[Depends(deps.get_current_active_superuser)],
    response_model=UserResponseObject,
)
async def update_user(*, id: int, session: deps.SessionDep, user_in: UserUpdate) -> Any:
    """
    Update some user.
    """
    logger = logging.getLogger("PATCH users/{id}")

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
    return user


@router.delete(
    "/{id}",
    tags=["Admin"],
    dependencies=[Depends(deps.get_current_active_superuser)],
    response_model=DefaultResponseMessage,
)
async def delete_user(
    *, id: int, session: deps.SessionDep, current_user: deps.CurrentUser
) -> Any:
    """
    Deactivate some user.
    """
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
    return DefaultResponseMessage(message="User deactivated successfully")
