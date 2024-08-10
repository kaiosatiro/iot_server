import logging
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from src.route.dependencies import create_device_access_token
from src.main import app


@pytest.fixture(scope="class")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as client:
        yield client


class TestListnerEndPoint:
    @pytest.fixture(scope="class")
    def token(self):
        token = create_device_access_token(1)
        return token
    
    def test_listener_endpoint(self, token:str, client: TestClient):

        response = client.get("/", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 202
        assert response.json() == {"message": "ok"}
        
