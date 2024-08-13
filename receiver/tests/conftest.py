from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture(scope="class", autouse=False)
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as client:
        yield client
