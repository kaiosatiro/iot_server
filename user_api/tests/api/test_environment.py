import pytest
from fastapi.testclient import TestClient

import src.crud as crud
from src.models import (
    EnvironmentCreation,
)


class TestGetEnvironment:
    @pytest.fixture(name="environmentsbatchrange", autouse=True, scope="class")
    def environmentsbatch(self, db, client: TestClient, normal_token_headers) -> tuple[int, int]:
        response = client.get("/users/me", headers=normal_token_headers)
        user_id = response.json()["id"]
        username = response.json()["username"]
        rng = 10
        for _ in range(rng):
            environment = EnvironmentCreation(name=f"Environment_{_}")
            crud.create_environment(db=db, environment_input=environment, owner_id=user_id)
        return {
            "range": rng, "user-id": user_id, "username": username
        }

    def test_get_environments(
            self,
            client: TestClient,
            normal_token_headers: dict,
            environmentsbatchrange
    ) -> None:

        response = client.get("/environments/user", headers=normal_token_headers)

        assert response.status_code == 200
        assert response.json()["count"] == environmentsbatchrange["range"], "Should be the count define in the fixture"
        assert response.json()["owner_id"] == environmentsbatchrange["user-id"], "Should be the last environment id"
        assert response.json()["username"] == environmentsbatchrange["username"], "Should be the last environment name"
        assert response.json()["data"], "Should return a list of environments"

    def test_get_environments_no_token(self, client: TestClient) -> None:
        response = client.get("/environments/user")
        assert response.status_code == 401

    def test_get_environments_no_environments(self, client: TestClient, superuser_token_headers: dict) -> None:
        response = client.get("/environments/user", headers=superuser_token_headers)
        assert response.status_code == 200
        assert response.json()["count"] == 0, "Should be 0"


class TestGetEnvironment:
    @pytest.fixture(autouse=True)
    def environment_id(self, db, client: TestClient, normal_token_headers) -> int:
        environment = EnvironmentCreation(name="Environment_1")
        response = client.post("/environments/", headers=normal_token_headers, json=environment.model_dump())
        return response.json()["id"]

    def test_get_environment(
            self,
            client: TestClient,
            normal_token_headers: dict,
            environment_id: int
    ) -> None:
        response = client.get(f"/environments/{environment_id}", headers=normal_token_headers)

        assert response.status_code == 200
        assert response.json()["id"] == environment_id

    def test_get_environment_no_token(self, client: TestClient, environment_id: int) -> None:
        response = client.get(f"/environments/{environment_id}")
        assert response.status_code == 401

    def test_get_wrong_environment(self, client: TestClient, normal_token_headers: dict) -> None:
        response = client.get("/environments/999999", headers=normal_token_headers)
        assert response.status_code == 404


class TestCreateEnvironment:
    def test_create_environment(
            self,
            client: TestClient,
            normal_token_headers: dict,
    ) -> None:
        environment = EnvironmentCreation(name="Environment_1")
        response = client.post("/environments/", headers=normal_token_headers, json=environment.model_dump())

        assert response.status_code == 201
        assert response.json()["name"] == environment.name

    def test_create_environment_no_token(self, client: TestClient) -> None:
        environment = EnvironmentCreation(name="Environment_1")
        response = client.post("/environments/", json=environment.model_dump())

        assert response.status_code == 401

    def test_create_environment_no_name(self, client: TestClient, normal_token_headers: dict) -> None:
        response = client.post("/environments/", headers=normal_token_headers, json={})

        assert response.status_code == 422

    def test_create_environment_no_environment(self, client: TestClient, normal_token_headers: dict) -> None:
        response = client.post("/environments/", headers=normal_token_headers)

        assert response.status_code == 422


class TestPatchEnvironment:
    @pytest.fixture(name="environment_id", autouse=True, scope="class")
    def environment_id(self, client: TestClient, normal_token_headers) -> int:
        environment = EnvironmentCreation(name="Environment_1")
        response = client.post("/environments/", headers=normal_token_headers, json=environment.model_dump())
        return response.json()["id"]

    def test_patch_environment(
            self,
            client: TestClient,
            normal_token_headers: dict,
            environment_id: int
    ) -> None:
        environment = EnvironmentCreation(name="Environment_2")
        response = client.patch(f"/environments/{environment_id}", headers=normal_token_headers, json=environment.model_dump())

        assert response.status_code == 200
        assert response.json()["name"] == environment.name

    def test_patch_environment_no_token(self, client: TestClient, environment_id: int) -> None:
        environment = EnvironmentCreation(name="Environment_2")
        response = client.patch(f"/environments/{environment_id}", json=environment.model_dump())

        assert response.status_code == 401

    @pytest.mark.skip("Not implemented")
    def test_patch_environment_no_name(self, client: TestClient, normal_token_headers: dict, environment_id: int) -> None:
        response = client.patch(f"/environments/{environment_id}", headers=normal_token_headers, json={})

        assert response.status_code == 422

    def test_patch_environment_no_environment(self, client: TestClient, normal_token_headers: dict, environment_id: int) -> None:
        response = client.patch(f"/environments/{environment_id}", headers=normal_token_headers)

        assert response.status_code == 422


class TestDeleteEnvironment:
    @pytest.fixture(name="environment_id", autouse=True, scope="class")
    def environment_id(self, client: TestClient, normal_token_headers) -> int:
        environment = EnvironmentCreation(name="Environment_1")
        response = client.post("/environments/", headers=normal_token_headers, json=environment.model_dump())
        return response.json()["id"]

    def test_delete_environment(
            self,
            client: TestClient,
            normal_token_headers: dict,
            environment_id: int
    ) -> None:
        response = client.delete(f"/environments/{environment_id}", headers=normal_token_headers)

        assert response.status_code == 200

    def test_delete_environment_no_token(self, client: TestClient, environment_id: int) -> None:
        response = client.delete(f"/environments/{environment_id}")

        assert response.status_code == 401

    def test_delete_environment_no_environment(self, client: TestClient, normal_token_headers: dict) -> None:
        response = client.delete("/environments/", headers=normal_token_headers)

        assert response.status_code == 405
