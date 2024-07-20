from collections.abc import Generator

import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from tests.utils.utils import random_email, random_lower_string


@pytest.fixture(name="db", autouse=True, scope="module")
def session_fixture() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture(name="userfix")
def user_fixture() -> dict:
    return {
        "email": random_email(),
        "username": random_lower_string(),
        "password": random_lower_string(),
        "about": random_lower_string(),
    }

@pytest.fixture(name="sitefix")
def site_fixture() -> dict:
    return {
        "name": random_lower_string(),
        "description": random_lower_string(),
    }

@pytest.fixture(name="devicefix")
def device_fixture() -> dict:
    return {
        "name": random_lower_string(),
        "model": random_lower_string(),
        "type": random_lower_string(),
        "description": random_lower_string(),
    }