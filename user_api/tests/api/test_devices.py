import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from src import crud
from src.models import Device, DeviceCreation, EnvironmentCreation, UserCreation


class TestGetDevices:
    @pytest.fixture(autouse=True, scope="class")
    def devicesbatch(self, db: Session, client: TestClient, normal_token_headers) -> tuple[int, int]:
        response = client.get("/users/me", headers=normal_token_headers)
        user_id = response.json()["id"]

        environment = EnvironmentCreation(name="Environment", description="Description")
        environment = crud.create_environment(
            db=db,
            environment_input=environment,
            owner_id=user_id
            )

        rng = 10
        for i in range(rng):
            device = DeviceCreation(
                owner_id=user_id,
                environment_id=environment.id,
                name=f"Device_{i}",
                model=f"Model{i}",
                type="Type",
                description="Description",
            )
            crud.create_device(db=db, device_input=device)

        return {
            "range": rng,
            "user_id": user_id,
            "username": response.json()["username"]
        }

    def test_get_devices(
            self,
            client: TestClient,
            normal_token_headers: dict,
            devicesbatch
    ) -> None:

        response = client.get("/devices/", headers=normal_token_headers)

        assert response.status_code == 200
        assert response.json()["count"] == devicesbatch["range"], "Define in the fixture"
        assert response.json()["owner_id"] == devicesbatch["user_id"], "Should be the last user id"
        assert response.json()["username"] == devicesbatch["username"], "Should be the last username"
        assert response.json()["data"], "Should return a list of devices"

    def test_get_devices_no_token(self, client: TestClient) -> None:
        response = client.get("/devices/")
        assert response.status_code == 401

    def test_get_devices_no_devices(self, client: TestClient, superuser_token_headers: dict) -> None:
        response = client.get("/devices/", headers=superuser_token_headers)
        assert response.status_code == 200
        assert response.json()["count"] == 0, "Should be 0"


class TestGetDevice:
    @pytest.fixture(autouse=True, scope="class")
    def devicesbatch(self, db: Session, client: TestClient, normal_token_headers) -> dict:
        response = client.get("/users/me", headers=normal_token_headers)
        user_id = response.json()["id"]

        environment = EnvironmentCreation(name="Environment", description="Description")
        environment = crud.create_environment(
            db=db,
            environment_input=environment,
            owner_id=user_id
            )

        device = DeviceCreation(
            owner_id=user_id,
            environment_id=environment.id,
            name="Device",
            model="Model",
            type="Type",
            description="Description",
        )
        device = crud.create_device(db=db, device_input=device)

        return {"device_id": device.id, "environment_id": environment.id, "user_id": user_id}

    def test_get_device(
            self,
            client: TestClient,
            normal_token_headers: dict,
            devicesbatch
    ) -> None:

        device_id = devicesbatch["device_id"]
        response = client.get(f"/devices/{device_id}", headers=normal_token_headers)

        assert response.status_code == 200
        assert response.json()["name"] == "Device"
        assert response.json()["token"]

    def test_get_device_no_token(self, client: TestClient) -> None:
        response = client.get("/devices/1")
        assert response.status_code == 401

    def test_get_device_not_found(
            self, client: TestClient, normal_token_headers: dict) -> None:
        response = client.get("/devices/999", headers=normal_token_headers)
        assert response.status_code == 404

    def test_get_device_wrong_user(
            self,
            db: Session, client: TestClient,
            normal_token_headers: dict) -> None:

        u = UserCreation(email="email", username="random_lower_string()", password="random_lower_string()")
        user = crud.create_user(db=db, user_input=u)
        s = EnvironmentCreation(name="Environment", description="Description")
        environment = crud.create_environment(db=db, environment_input=s, owner_id=user.id)

        d = DeviceCreation(
            owner_id=user.id,  # <<< user ID from different user to be use in the request
            environment_id=environment.id,
            name="Device",
            model="Model",
            type="Type",
            description="Description",
        )
        device = crud.create_device(db=db, device_input=d)

        response = client.get(f"/devices/{device.id}", headers=normal_token_headers)
        assert response.status_code == 403


class TestGetDevicePerEnvironment:
    @pytest.fixture(autouse=True, scope="class")
    def devicesbatch(self, db: Session, client: TestClient, normal_token_headers) -> dict:
        response = client.get("/users/me", headers=normal_token_headers)
        user_id = response.json()["id"]

        environment = EnvironmentCreation(name="Environment", description="Description")
        environment = crud.create_environment(
            db=db,
            environment_input=environment,
            owner_id=user_id
            )

        rng = 10
        for i in range(rng):
            device = DeviceCreation(
                owner_id=user_id,
                environment_id=environment.id,
                name=f"Device_{i}",
                model=f"Model{i}",
                type="Type",
                description="Description",
            )
            crud.create_device(db=db, device_input=device)

        return {
            "range": rng,
            "environment_id": environment.id,
            "environment-name": environment.name,
            "user_id": user_id,
            "username": response.json()["username"]
        }

    def test_get_devices_per_environment(
            self,
            client: TestClient,
            normal_token_headers: dict,
            devicesbatch
    ) -> None:
        environment_id = devicesbatch["environment_id"]
        response = client.get(f"/devices/environment/{environment_id}", headers=normal_token_headers)

        assert response.status_code == 200
        assert response.json()["count"] == devicesbatch["range"], "Define in the fixture"
        assert response.json()["environment_id"] == environment_id, "Should be the last environment id"
        assert response.json()["environment_name"] == devicesbatch["environment-name"], "Should be the last environment name"
        assert response.json()["owner_id"] == devicesbatch["user_id"], "Should be the last user id"
        assert response.json()["username"] == devicesbatch["username"], "Should be the last username"
        assert response.json()["data"], "Should return a list of devices"

    def test_get_devices_per_environment_no_token(self, client: TestClient) -> None:
        response = client.get("/devices/environment/1")

        assert response.status_code == 401

    def test_get_devices_not_found_environment(
            self,
            client: TestClient, normal_token_headers: dict) -> None:
        response = client.get("/devices/environment/999", headers=normal_token_headers)

        assert response.status_code == 404

    def test_get_empty_devices_list_per_environment(
            self,
            db: Session,
            client: TestClient,
            normal_token_headers: dict,
            devicesbatch
    ) -> None:
        user_id = devicesbatch["user_id"]
        environment = EnvironmentCreation(name="Environment", description="Description")
        environment = crud.create_environment(
            db=db,
            environment_input=environment,
            owner_id=user_id
            )
        response = client.get(f"/devices/environment/{environment.id}", headers=normal_token_headers)

        assert response.status_code == 200
        assert response.json()["count"] == 0, "Should be 0"
        assert response.json()["data"] == [], "Should return an empty list"


class TestCreateDevice:
    @pytest.fixture(autouse=True, scope="class")
    def devicesbatch(self, db: Session, client: TestClient, normal_token_headers) -> dict:
        response = client.get("/users/me", headers=normal_token_headers)
        user_id = response.json()["id"]

        environment = EnvironmentCreation(name="Environment", description="Description")
        environment = crud.create_environment(db=db, environment_input=environment, owner_id=user_id)

        return {"environment_id": environment.id, "user_id": user_id}

    def test_create_device(
            self,
            db: Session, client: TestClient,
            devicesbatch, normal_token_headers: dict
    ) -> None:

        user_id = devicesbatch["user_id"]
        environment = crud.create_environment(
            db=db,
            environment_input=EnvironmentCreation(name="Environment", description="Description"),
            owner_id=user_id
            )

        device = {
            "owner_id": user_id,
            "environment_id": environment.id,
            "name": "Device",
            "model": "Model",
            "type": "Type",
            "description": "Description",
        }
        response = client.post("/devices/environment", headers=normal_token_headers, json=device)

        assert response.status_code == 201
        assert response.json()["name"] == "Device"
        assert response.json()["token"]

        #  Without user_id
        device = {
            "environment_id": environment.id,
            "name": "Device",
            "model": "Model",
            "type": "Type",
            "description": "Description",
        }
        response = client.post("/devices/environment", headers=normal_token_headers, json=device)

        assert response.status_code == 201
        assert response.json()["name"] == "Device"
        assert response.json()["token"]

    def test_create_device_no_token(self, client: TestClient) -> None:
        response = client.post("/devices/environment")
        assert response.status_code == 401

    def test_create_device_environment_do_not_exists(
            self, client: TestClient, normal_token_headers: dict) -> None:
        device = {
            "owner_id": 1,
            "environment_id": 999,
            "name": "Device",
            "model": "Model",
            "type": "Type",
            "description": "Description",
        }
        response = client.post("/devices/environment", headers=normal_token_headers, json=device)
        assert response.status_code == 404

    def test_create_device_wrong_user(
            self,
            db: Session, client: TestClient,
            normal_token_headers: dict) -> None:

        u = UserCreation(email="email", username="random_lower_string()", password="random_lower_string()")
        user = crud.create_user(db=db, user_input=u)
        s = EnvironmentCreation(name="Environment", description="Description")
        environment = crud.create_environment(db=db, environment_input=s, owner_id=user.id)

        device = {
            "environment_id": environment.id,  # <<< environment ID from different user
            "name": "Device",
            "model": "Model",
            "type": "Type",
            "description": "Description",
        }
        response = client.post("/devices/environment", headers=normal_token_headers, json=device)

        assert response.status_code == 403

    def test_create_device_no_environment_id(
            self, client: TestClient, normal_token_headers: dict) -> None:
        device = {
            "name": "Device",
            "model": "Model",
            "type": "Type",
            "description": "Description",
        }
        response = client.post("/devices/environment", headers=normal_token_headers, json=device)

        assert response.status_code == 422


class TestUpdateDevice:
    @pytest.fixture(autouse=True, scope="class")
    def devicesbatch(self, db: Session, client: TestClient, normal_token_headers) -> dict:
        response = client.get("/users/me", headers=normal_token_headers)
        user_id = response.json()["id"]

        environment = EnvironmentCreation(name="Environment", description="Description")
        environment = crud.create_environment(db=db, environment_input=environment, owner_id=user_id)

        device = DeviceCreation(
            owner_id=user_id,
            environment_id=environment.id,
            name="Device",
            model="Model",
            type="Type",
            description="Description",
        )
        device = crud.create_device(db=db, device_input=device)

        return {"device_id": device.id, "environment_id": environment.id, "user_id": user_id}

    def test_update_device(
            self, client: TestClient,
            devicesbatch, normal_token_headers: dict) -> None:

        device_id = devicesbatch["device_id"]

        device = {
            "name": "New Device",
            "model": "New Model",
            "type": "New Type",
            "description": "New Description",
        }
        response = client.patch(f"/devices/{device_id}", headers=normal_token_headers, json=device)

        assert response.status_code == 200
        assert response.json()["name"] == "New Device"

    def test_update_device_environment_id(
            self, client: TestClient, db,
            devicesbatch, normal_token_headers: dict) -> None:

        device_id = devicesbatch["device_id"]
        # Create a new environment
        environment = EnvironmentCreation(name="Environment", description="Description")
        new_environment = crud.create_environment(db=db, environment_input=environment, owner_id=devicesbatch["user_id"])

        device = {
            "environment_id": new_environment.id,
        }
        response = client.patch(f"/devices/{device_id}", headers=normal_token_headers, json=device)

        assert response.status_code == 200
        assert response.json()["environment_id"] == new_environment.id

    def test_update_device_wrong_environment_id(
            self, client: TestClient,
            devicesbatch, normal_token_headers: dict) -> None:

        device_id = devicesbatch["device_id"]
        device = {
            "environment_id": 999,
        }

        response = client.patch(f"/devices/{device_id}", headers=normal_token_headers, json=device)
        assert response.status_code == 404

    def test_update_device_no_token(self, client: TestClient) -> None:
        response = client.patch("/devices/1")
        assert response.status_code == 401

    def test_update_device_not_found(
            self, client: TestClient, normal_token_headers: dict) -> None:
        device = {
            "name": "New Device",
            "model": "New Model",
            "type": "New Type",
            "description": "New Description",
        }
        response = client.patch("/devices/999", headers=normal_token_headers, json=device)
        assert response.status_code == 404

    def test_update_device_wrong_user(
            self,
            db: Session, client: TestClient,
            normal_token_headers: dict) -> None:

        u = UserCreation(email="email", username="random_lower_string()", password="random_lower_string()")
        user = crud.create_user(db=db, user_input=u)
        s = EnvironmentCreation(name="Environment", description="Description")
        environment = crud.create_environment(db=db, environment_input=s, owner_id=user.id)

        d = DeviceCreation(
            owner_id=user.id,  # <<< user ID from different user to be use in the request
            environment_id=environment.id,
            name="Device",
            model="Model",
            type="Type",
            description="Description",
        )
        device = crud.create_device(db=db, device_input=d)

        response = client.patch(f"/devices/{device.id}", headers=normal_token_headers, json=d.model_dump())
        assert response.status_code == 403


class TestDeleteDevice:
    @pytest.fixture()
    def devicesbatch(self, db: Session, client: TestClient, normal_token_headers) -> tuple[int, int]:
        response = client.get("/users/me", headers=normal_token_headers)
        user_id = response.json()["id"]

        environment = EnvironmentCreation(name="Environment", description="Description")
        environment = crud.create_environment(db=db, environment_input=environment, owner_id=user_id)

        device = DeviceCreation(
                owner_id=user_id,
                environment_id=environment.id,
                name="Device",
                model="Model",
                type="Type",
                description="Description",
            )
        device = crud.create_device(db=db, device_input=device)

        return {"environment_id": environment.id, "user_id": user_id, "device_id": device.id}

    def test_delete_device(
            self, client: TestClient, db: Session,
            devicesbatch, normal_token_headers: dict) -> None:

        device_id = devicesbatch["device_id"]

        response = client.delete(f"/devices/{device_id}", headers=normal_token_headers)
        assert response.status_code == 200
        assert not db.get(Device, device_id)

    def test_delete_device_no_token(self, client: TestClient) -> None:
        response = client.delete("/devices/1")
        assert response.status_code == 401

    def test_delete_device_not_found(
            self, client: TestClient, normal_token_headers: dict) -> None:
        response = client.delete("/devices/999", headers=normal_token_headers)
        assert response.status_code == 404

    def test_delete_device_wrong_user(
            self,
            db: Session, client: TestClient,
            normal_token_headers: dict) -> None:

        u = UserCreation(email="email", username="random_lower_string()", password="random_lower_string()")
        user = crud.create_user(db=db, user_input=u)
        s = EnvironmentCreation(name="Environment", description="Description")
        environment = crud.create_environment(db=db, environment_input=s, owner_id=user.id)

        d = DeviceCreation(
            owner_id=user.id,  # <<< user ID from different user to be use in the request
            environment_id=environment.id,
            name="Device",
            model="Model",
            type="Type",
            description="Description",
        )
        device = crud.create_device(db=db, device_input=d)

        response = client.delete(f"/devices/{device.id}", headers=normal_token_headers)
        assert response.status_code == 403


class TestDeleteAllDevice:
    @pytest.fixture()
    def devicesbatch(self, db: Session, client: TestClient, normal_token_headers) -> tuple[int, int]:
        response = client.get("/users/me", headers=normal_token_headers)
        user_id = response.json()["id"]

        environment = EnvironmentCreation(name="Environment", description="Description")
        environment = crud.create_environment(db=db, environment_input=environment, owner_id=user_id)

        rng = 10
        for i in range(rng):
            device = DeviceCreation(
                owner_id=user_id,
                environment_id=environment.id,
                name=f"Device_{i}",
                model=f"Model{i}",
                type="Type",
                description="Description",
            )
            crud.create_device(db=db, device_input=device)

        return {"range": rng, "environment_id": environment.id, "user_id": user_id}

    def test_delete_all_devices(
            self, client: TestClient, db: Session,
            devicesbatch, normal_token_headers: dict) -> None:

        environment_id = devicesbatch["environment_id"]

        response = client.delete(f"/devices/environment/{environment_id}", headers=normal_token_headers)
        assert response.status_code == 200

        statement = select(Device).where(Device.environment_id == environment_id)
        results = db.exec(statement)
        assert not results.all()

    def test_delete_all_devices_no_token(self, client: TestClient) -> None:
        response = client.delete("/devices/environment/1")
        assert response.status_code == 401

    def test_delete_all_devices_not_found(
            self, client: TestClient, normal_token_headers: dict) -> None:
        response = client.delete("/devices/environment/999", headers=normal_token_headers)
        assert response.status_code == 404

    def test_delete_all_devices_wrong_user(
            self,
            db: Session, client: TestClient,
            normal_token_headers: dict) -> None:

        u = UserCreation(email="email", username="random_lower_string()", password="random_lower_string()")
        user = crud.create_user(db=db, user_input=u)
        s = EnvironmentCreation(name="Environment", description="Description")
        environment = crud.create_environment(db=db, environment_input=s, owner_id=user.id)

        d = DeviceCreation(
            owner_id=user.id,
            environment_id=environment.id,  # <<< user ID from different user to be use in the request
            name="Device",
            model="Model",
            type="Type",
            description="Description",
        )
        crud.create_device(db=db, device_input=d)

        response = client.delete(f"/devices/environment/{environment.id}", headers=normal_token_headers)
        assert response.status_code == 403
