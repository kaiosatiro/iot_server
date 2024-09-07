from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, delete

from src import crud
from src.core.config import settings
from src.core.db import engine, init_db
from src.main import app
from src.models import (
    Device,
    DeviceCreation,
    Message,
    MessageCreation,
    Site,
    SiteCreation,
    User,
    UserCreation,
)

# from sqlmodel import SQLModel, create_engine
# from sqlmodel.pool import StaticPool
from tests.utils import random_email, random_lower_string


# ----------------------------- Sessions --------------------------------
@pytest.fixture(name="db", autouse=True, scope="class")  # scope="session"
def session_fixture() -> Generator[Session, None, None]:
    # engine = create_engine(
    #     "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    # )
    # SQLModel.metadata.drop_all(engine)
    # SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        init_db(session)
        yield session
        statement = delete(Message)
        session.exec(statement)
        statement = delete(Device)
        session.exec(statement)
        statement = delete(Site)
        session.exec(statement)
        statement = delete(User)
        session.exec(statement)
        session.commit()


@pytest.fixture(scope="class")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as client:
        yield client


# ----------------------------- Superuser --------------------------------
@pytest.fixture(name="superuserfix")
def superuser_fixture() -> dict:
    return {
        "email": settings.FIRST_SUPERUSER_EMAIL,
        "username": settings.FIRST_SUPERUSERNAME,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }


@pytest.fixture(scope="class")
def superuser_token_headers(client: TestClient) -> dict[str, str]:
    login_data = {
        "username": settings.FIRST_SUPERUSERNAME,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    response = client.post("/access-token", data=login_data)
    tokens = response.json()
    headers = {"Authorization": f"Bearer {tokens["access_token"]}"}
    return headers


# ----------------------------- Normal User --------------------------------
@pytest.fixture(scope="class")
def normaluser_fixture(db: Session) -> dict:
    userdict = {
        "email": random_email(),
        "username": random_lower_string(),
        "password": random_lower_string(),
        "about": random_lower_string(),
    }
    user_in = UserCreation(**userdict)
    crud.create_user(db=db, user_input=user_in)
    return userdict


@pytest.fixture(scope="class")
def normal_token_headers(normaluser_fixture, client: TestClient) -> dict[str, str]:
    login_data = {
        "username": normaluser_fixture["username"],
        "password": normaluser_fixture["password"],
    }
    response = client.post("/access-token", data=login_data)
    tokens = response.json()
    headers = {"Authorization": f"Bearer {tokens["access_token"]}"}
    return headers


# ----------------------------- Model Fixtures --------------------------------
@pytest.fixture(name="userfix", scope="module")
def user_fixture() -> dict:
    return {
        "email": random_email(),
        "username": random_lower_string(),
        "password": random_lower_string(),
        "about": random_lower_string(),
    }


@pytest.fixture(name="sitefix", scope="module")
def site_fixture() -> dict:
    return {
        "name": random_lower_string(),
        "description": random_lower_string(),
    }


@pytest.fixture(name="devicefix", scope="module")
def device_fixture() -> dict:
    return {
        "name": random_lower_string(),
        "model": random_lower_string(),
        "type": random_lower_string(),
        "description": random_lower_string(),
    }


# ----------------------------- For Messages --------------------------------
@pytest.fixture(name="messagesbatchfix", scope="class")
def messages_batch_fixture(db, userfix, sitefix, devicefix) -> tuple[int | None, int]:
    user_in = UserCreation(**userfix)
    user = crud.create_user(db=db, user_input=user_in)

    site_in = SiteCreation(**sitefix)
    site = crud.create_site(db=db, site_input=site_in, owner_id=user.id)

    device_in = DeviceCreation(**devicefix, owner_id=user.id, site_id=site.id)
    device = crud.create_device(db=db, device_input=device_in)

    messages = []
    range_number = 100
    for _ in range(range_number):
        message = MessageCreation(
            message={
                "deviceId": random_lower_string(),
                "sensorId": random_lower_string(),
                "timestamp": random_lower_string(),
                "type": random_lower_string(),
                "unit": random_lower_string(),
                "value": 45.2,
            },
            device_id=device.id,
        )
        message_in = Message.model_validate(message)
        messages.append(message_in)

    db.add_all(messages)
    db.commit()

    return device.id, range_number
