from time import sleep

import pytest
from fastapi.testclient import TestClient

from src.route.dependencies import create_device_access_token
from src.models import MessageTest


class TestListnerEndPoint:
    @pytest.fixture(scope="class")
    def token(self):
        token = create_device_access_token(1)
        return token

    def test_listener_endpoint_simple_payload(self, token: str, client: TestClient):
        payload = MessageTest(message="Hello!")
        # payload = json.dumps(payload)

        response = client.post(
            "/", headers={"Authorization": f"Bearer {token}"}, json=payload.model_dump()
        )
        assert response.status_code == 202

    def test_listener_diferent_payload(self, token: str, client: TestClient):
        payload = {
            "id": 1,
            "body": {
                "message": "Hello!",
                "other": "world"
            }
        }

        response = client.post("/", headers={"Authorization": f"Bearer {token}"}, json=payload)
        assert response.status_code == 202

    def test_listener_endpoint_invalid_token(self, client: TestClient):
        payload = MessageTest(message="Hello!")
        response = client.post("/", headers={"Authorization": "Bearer invalid_token"}, json=payload.model_dump())
        assert response.status_code == 403

    def test_listener_without_payload(self, token: str, client: TestClient):
        response = client.post("/", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 422

        sleep(3)
    
    def test_listener_with_token_not_bearer(self, token: str, client: TestClient):
        response = client.post("/", headers={"Authorization": token})
        assert response.status_code == 401

        sleep(3)


class TestTestToken:
    @pytest.fixture(scope="class")
    def token(self):
        token = create_device_access_token(1)
        return token

    def test_test_token(self, client: TestClient, token: str) -> None:
        response = client.post("/test-token", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200

    def test_test_token_invalid(self, client: TestClient) -> None:
        response = client.post("/test-token", headers={"Authorization": "Bearer invalid_token"},)
        assert response.status_code == 403
    
    def test_test_token_not_bearer(self, client: TestClient) -> None:
        response = client.post("/test-token", headers={"Authorization ": "invalid_token"},)
        assert response.status_code == 401