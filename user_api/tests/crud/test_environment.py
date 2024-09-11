from sqlmodel import Session

from src import crud
from src.models import (
    Environment,
    EnvironmentCreation,
    EnvironmentUpdate,
    UserCreation,
)
from tests.utils import random_lower_string


def test_create_environment(db: Session, userfix: dict, environmentfix: dict) -> None:
    user_in = UserCreation(**userfix)
    user = crud.create_user(db=db, user_input=user_in)
    environment_in = EnvironmentCreation(**environmentfix)
    environment = crud.create_environment(db=db, environment_input=environment_in, owner_id=user.id)

    assert (
        environment.name == environmentfix["name"]
    ), f"environment.name: {environment.name}, environmentfix['name']: {environmentfix['name']}"
    assert (
        environment.description == environmentfix["description"]
    ), f"environment.description: {environment.description}, environmentfix['description']: {environmentfix['description']}"
    assert environment.owner_id == user.id, f"environment.owner_id: {environment.owner_id}, user.id: {user.id}"


def test_update_environment(db: Session, userfix: dict, environmentfix: dict) -> None:
    user_in = UserCreation(**userfix)
    user = crud.create_user(db=db, user_input=user_in)
    environment_in = EnvironmentCreation(**environmentfix)
    environment = crud.create_environment(db=db, environment_input=environment_in, owner_id=user.id)
    environment_update = EnvironmentUpdate(
        name=random_lower_string(),
    )
    environment_seek = crud.update_environment(db=db, db_environment=environment, environment_new_input=environment_update)

    assert (
        environment_seek.name == environment_update.name
    ), f"environment_seek.name: {environment_seek.name}, environment_update.name: {environment_update.name}"
    assert (
        environment_seek.owner_id == user.id
    ), f"environment_seek.owner_id: {environment_seek.owner_id}, user.id: {user.id}"
    assert environment_seek.id == environment.id, f"environment_seek.id: {environment_seek.id}, environment.id: {environment.id}"

    environment_update2 = EnvironmentUpdate(description=random_lower_string())
    environment3 = crud.update_environment(db=db, db_environment=environment, environment_new_input=environment_update2)

    assert (
        environment3.description == environment_update2.description
    ), f"environment3.description: {environment3.description}, environment_update2.desc: {environment_update2.description}"
    assert (
        environment3.owner_id == user.id
    ), f"environment3.owner_id: {environment3.owner_id}, user.id: {user.id}"


def test_get_environment_by_name(db: Session, userfix: dict, environmentfix: dict) -> None:
    user_in = UserCreation(**userfix)
    user = crud.create_user(db=db, user_input=user_in)
    environment_in = EnvironmentCreation(**environmentfix)
    environment = crud.create_environment(db=db, environment_input=environment_in, owner_id=user.id)
    environment_seek = crud.get_environment_by_name(db=db, name=environmentfix["name"])

    assert environment_seek
    assert (
        environment_seek.name == environment.name
    ), f"environment_seek.name: {environment_seek.name}, environment.name: {environment.name}"
    assert (
        environment_seek.description == environment.description
    ), f"environment_seek.description: {environment_seek.description}, environment.description: {environment.description}"
    assert (
        environment_seek.owner_id == user.id
    ), f"environment_seek.owner_id: {environment_seek.owner_id}, user.id: {user.id}"
    assert environment_seek.id == environment.id, f"environment_seek.id: {environment_seek.id}, environment.id: {environment.id}"


def test_get_environment_by_name_none(db: Session, environmentfix: dict) -> None:
    environment_seek = crud.get_environment_by_name(db=db, name=environmentfix["name"])
    assert not environment_seek
    assert environment_seek is None, f"environment_seek: {environment_seek}"


def test_get_environments_by_owner_id(db: Session, userfix: dict, environmentfix: dict) -> None:
    user_in = UserCreation(**userfix)
    user = crud.create_user(db=db, user_input=user_in)
    environment_in = EnvironmentCreation(**environmentfix)
    environment = crud.create_environment(db=db, environment_input=environment_in, owner_id=user.id)
    environment_seek = crud.get_environments_by_owner_id(db=db, owner_id=user.id)

    assert environment_seek
    assert (
        environment_seek[0].name == environment.name
    ), f"environment_seek[0].name: {environment_seek[0].name}, environment.name: {environment.name}"
    assert (
        environment_seek[0].description == environment.description
    ), f"environment_seek[0].description: {environment_seek[0].description}, environment.description: {environment.description}"
    assert (
        environment_seek[0].owner_id == user.id
    ), f"environment_seek[0].owner_id: {environment_seek[0].owner_id}, user.id: {user.id}"
    assert (
        environment_seek[0].id == environment.id
    ), f"environment_seek[0].id: {environment_seek[0].id}, environment.id: {environment.id}"

    environment_in = EnvironmentCreation(**environmentfix)
    environment = crud.create_environment(db=db, environment_input=environment_in, owner_id=user.id)
    environment_seek = crud.get_environments_by_owner_id(db=db, owner_id=user.id)

    assert (
        environment_seek[1].name == environment.name
    ), f"environment_seek[1].name: {environment_seek[1].name}, environment.name: {environment.name}"
    assert (
        environment_seek[1].description == environment.description
    ), f"environment_seek[1].description: {environment_seek[1].description}, environment.description: {environment.description}"
    assert (
        environment_seek[1].owner_id == user.id
    ), f"environment_seek[1].owner_id: {environment_seek[1].owner_id}, user.id: {user.id}"
    assert (
        environment_seek[1].id == environment.id
    ), f"environment_seek[1].id: {environment_seek[1].id}, environment.id: {environment.id}"


def test_delete_environment(db: Session, userfix: dict, environmentfix: dict) -> None:
    user_in = UserCreation(**userfix)
    user = crud.create_user(db=db, user_input=user_in)
    environment_in = EnvironmentCreation(**environmentfix)
    environment = crud.create_environment(db=db, environment_input=environment_in, owner_id=user.id)

    environment_seek = db.get(Environment, environment.id)

    assert environment_seek
    assert (
        environment_seek.name == environment_in.name
    ), f"environment_seek.name: {environment_seek.name}, environment_in.name: {environment_in.name}"

    crud.delete_environment(db=db, environment=environment)

    assert not db.get(Environment, environment.id), "environment should be deleted"
    assert not crud.get_environment_by_name(
        db=db, name=environmentfix["name"]
    ), "environment should be deleted"


def test_delete_environments_from_user(db: Session, userfix: dict, environmentfix: dict) -> None:
    user_in = UserCreation(**userfix)
    user = crud.create_user(db=db, user_input=user_in)

    for _ in range(3):
        environment_in = EnvironmentCreation(**environmentfix)
        crud.create_environment(db=db, environment_input=environment_in, owner_id=user.id)

    environment_seek = crud.get_environments_by_owner_id(db=db, owner_id=user.id)
    environment_seek_count = len(environment_seek)

    assert environment_seek_count == 3, f"environment_seek_count: {environment_seek_count}"

    crud.delete_environments_from_user(db=db, owner_id=user.id)

    environment_seek = crud.get_environments_by_owner_id(db=db, owner_id=user.id)

    assert not environment_seek, f"environment_seek: {environment_seek}"
    assert environment_seek == [], f"environment_seek: {environment_seek}"
