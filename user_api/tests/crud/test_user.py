from sqlmodel import Session

from tests.utils.utils import random_email, random_lower_string
from src.models import UserCreate, UserUpdate
from src.core.security import verify_password
from src import crud


def test_create_user(db: Session, userfix: dict) -> None:
    user_in = UserCreate(**userfix)
    user_out = crud.create_user(db=db, user_input=user_in)

    assert user_out.email == userfix["email"], f"user_out.email: {user_out.email}, userfix['email']: {userfix['email']}"
    assert user_out.username == userfix["username"], f"user_out.username: {user_out.username}, userfix['username']: {userfix['username']}"
    assert user_out.about == userfix["about"], f"user_out.about: {user_out.about}, userfix['about']: {userfix['about']}"
    assert hasattr(user_out, 'hashed_password'), f"hashed_password not in user_out"

def test_update_user(db: Session, userfix: dict) -> None:
    old_user_in = UserCreate(**userfix)
    old_user = crud.create_user(db=db, user_input=old_user_in)
    new_email = random_email()
    new_username = random_lower_string()
    new_about = random_lower_string()
    new_user_in = UserUpdate(email=new_email, username=new_username, about=new_about)
    new_user = crud.update_user(db=db, db_user=old_user, user_new_input=new_user_in)

    assert new_user.email == new_email, f"new_user.email: {new_user.email}, new_email: {new_email}"
    assert new_user.username == new_username, f"new_user.username: {new_user.username}, new_username: {new_username}"
    assert new_user.about == new_about, f"new_user.about: {new_user.about}, new_about: {new_about}"


def test_get_user_by_email(db: Session, userfix: dict) -> None:
    user_in = UserCreate(**userfix)
    user = crud.create_user(db=db, user_input=user_in)
    seek_user = crud.get_user_by_email(db=db, email=userfix["email"])

    assert seek_user.email == user.email, f"seek_user.email: {seek_user.email}, user.email: {user.email}"


def test_get_user_by_email_none(db: Session, userfix: dict) -> None:
    seek_user = crud.get_user_by_email(db=db, email=userfix["email"])

    assert seek_user == None, "Should be None"

def test_update_password(db: Session, userfix: dict) -> None:
    user_in = UserCreate(**userfix)
    user_out = crud.create_user(db=db, user_input=user_in)

    new_password = random_lower_string()
    user = crud.update_password(db=db, user=user_out, password=new_password)

    assert verify_password(new_password, user.hashed_password), f"Password not updated"
    assert not verify_password(userfix["password"], user.hashed_password), f"Old password still works"

def test_deactivate_user(db: Session, userfix: dict) -> None:
    user_in = UserCreate(**userfix)
    user_out = crud.create_user(db=db, user_input=user_in)

    user = crud.deactivate_user(db=db, user=user_out)

    assert not user.is_active, f"User is still active"
    assert user.is_active == False, f"User is still active"