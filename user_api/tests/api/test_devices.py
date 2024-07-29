import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from src import crud
from src.models import Device, DeviceCreation, SiteCreation, UserCreation


class TestGetDevices:
    @pytest.fixture(autouse=True, scope="class")
    def devicesbatch(self, db: Session, client: TestClient, normal_token_headers) -> tuple[int, int]:
        response = client.get("/users/me", headers=normal_token_headers)
        user_id = response.json()["id"]

        site = SiteCreation(name="Site", description="Description")
        site = crud.create_site(
            db=db,
            site_input=site,
            user_id=user_id
            )

        rng = 10
        for i in range(rng):
            device = DeviceCreation(
                user_id=user_id,
                site_id=site.id,
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
        assert response.json()["user_id"] == devicesbatch["user_id"], "Should be the last user id"
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

        site = SiteCreation(name="Site", description="Description")
        site = crud.create_site(
            db=db,
            site_input=site,
            user_id=user_id
            )

        device = DeviceCreation(
            user_id=user_id,
            site_id=site.id,
            name="Device",
            model="Model",
            type="Type",
            description="Description",
        )
        device = crud.create_device(db=db, device_input=device)

        return {"device_id": device.id, "site_id": site.id, "user_id": user_id}

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
        s = SiteCreation(name="Site", description="Description")
        site = crud.create_site(db=db, site_input=s, user_id=user.id)

        d = DeviceCreation(
            user_id=user.id, # <<< user ID from different user to be use in the request
            site_id=site.id,
            name="Device",
            model="Model",
            type="Type",
            description="Description",
        )
        device = crud.create_device(db=db, device_input=d)

        response = client.get(f"/devices/{device.id}", headers=normal_token_headers)
        assert response.status_code == 403


class TestGetDevicePerSite:
    @pytest.fixture(autouse=True, scope="class")
    def devicesbatch(self, db: Session, client: TestClient, normal_token_headers) -> dict:
        response = client.get("/users/me", headers=normal_token_headers)
        user_id = response.json()["id"]

        site = SiteCreation(name="Site", description="Description")
        site = crud.create_site(
            db=db,
            site_input=site,
            user_id=user_id
            )

        rng = 10
        for i in range(rng):
            device = DeviceCreation(
                user_id=user_id,
                site_id=site.id,
                name=f"Device_{i}",
                model=f"Model{i}",
                type="Type",
                description="Description",
            )
            crud.create_device(db=db, device_input=device)

        return {
            "range": rng,
            "site_id": site.id,
            "site-name":site.name ,
            "user_id": user_id,
            "username": response.json()["username"]
        }
    

    def test_get_devices_per_site(
            self,
            client: TestClient,
            normal_token_headers: dict,
            devicesbatch
    ) -> None:
        site_id = devicesbatch["site_id"]
        response = client.get(f"/devices/site/{site_id}", headers=normal_token_headers)

        assert response.status_code == 200
        assert response.json()["count"] == devicesbatch["range"], "Define in the fixture"
        assert response.json()["site_id"] == site_id, "Should be the last site id"
        assert response.json()["site_name"] == devicesbatch["site-name"], "Should be the last site name"
        assert response.json()["user_id"] == devicesbatch["user_id"], "Should be the last user id"
        assert response.json()["username"] == devicesbatch["username"], "Should be the last username"
        assert response.json()["data"], "Should return a list of devices"

    def test_get_devices_per_site_no_token(self, client: TestClient) -> None:
        response = client.get("/devices/site/1")

        assert response.status_code == 401

    def test_get_devices_not_found_site(
            self,
            client: TestClient, normal_token_headers: dict) -> None:
        response = client.get("/devices/site/999", headers=normal_token_headers)

        assert response.status_code == 404

    def test_get_empty_devices_list_per_site(
            self,
            db: Session,
            client: TestClient,
            normal_token_headers: dict,
            devicesbatch
    ) -> None:
        user_id = devicesbatch["user_id"]
        site = SiteCreation(name="Site", description="Description")
        site = crud.create_site(
            db=db,
            site_input=site,
            user_id=user_id
            )
        response = client.get(f"/devices/site/{site.id}", headers=normal_token_headers)

        assert response.status_code == 200
        assert response.json()["count"] == 0, "Should be 0"
        assert response.json()["data"] == [], "Should return an empty list"


class TestCreateDevice:
    @pytest.fixture(autouse=True, scope="class")
    def devicesbatch(self, db: Session, client: TestClient, normal_token_headers) -> dict:
        response = client.get("/users/me", headers=normal_token_headers)
        user_id = response.json()["id"]

        site = SiteCreation(name="Site", description="Description")
        site = crud.create_site(db=db, site_input=site, user_id=user_id)

        return {"site_id": site.id, "user_id": user_id}

    def test_create_device(
            self,
            db: Session, client: TestClient,
            devicesbatch, normal_token_headers: dict
        ) -> None:

        user_id = devicesbatch["user_id"]
        site = crud.create_site(
            db=db,
            site_input=SiteCreation(name="Site", description="Description"),
            user_id=user_id
            )

        device = {
            "user_id": user_id,
            "site_id": site.id,
            "name": "Device",
            "model": "Model",
            "type": "Type",
            "description": "Description",
        }
        response = client.post("/devices/site", headers=normal_token_headers, json=device)

        assert response.status_code == 201
        assert response.json()["name"] == "Device"

        #  Without user_id
        device = {
            "site_id": site.id,
            "name": "Device",
            "model": "Model",
            "type": "Type",
            "description": "Description",
        }
        response = client.post("/devices/site", headers=normal_token_headers, json=device)

        assert response.status_code == 201
        assert response.json()["name"] == "Device"

    def test_create_device_no_token(self, client: TestClient) -> None:
        response = client.post("/devices/site")
        assert response.status_code == 401

    def test_create_device_site_do_not_exists(
            self, client: TestClient, normal_token_headers: dict) -> None:
        device = {
            "user_id": 1,
            "site_id": 999,
            "name": "Device",
            "model": "Model",
            "type": "Type",
            "description": "Description",
        }
        response = client.post("/devices/site", headers=normal_token_headers, json=device)
        assert response.status_code == 404

    def test_create_device_wrong_user(
            self,
            db: Session, client: TestClient,
            normal_token_headers: dict) -> None:

        u = UserCreation(email="email", username="random_lower_string()", password="random_lower_string()")
        user = crud.create_user(db=db, user_input=u)
        s = SiteCreation(name="Site", description="Description")
        site = crud.create_site(db=db, site_input=s, user_id=user.id)

        device = {
            "site_id": site.id,  # <<< site ID from different user
            "name": "Device",
            "model": "Model",
            "type": "Type",
            "description": "Description",
        }
        response = client.post("/devices/site", headers=normal_token_headers, json=device)

        assert response.status_code == 403

    def test_create_device_no_site_id(
            self, client: TestClient, normal_token_headers: dict) -> None:
        device = {
            "name": "Device",
            "model": "Model",
            "type": "Type",
            "description": "Description",
        }
        response = client.post("/devices/site", headers=normal_token_headers, json=device)

        assert response.status_code == 422


class TestUpdateDevice:
    @pytest.fixture(autouse=True, scope="class")
    def devicesbatch(self, db: Session, client: TestClient, normal_token_headers) -> dict:
        response = client.get("/users/me", headers=normal_token_headers)
        user_id = response.json()["id"]

        site = SiteCreation(name="Site", description="Description")
        site = crud.create_site(db=db, site_input=site, user_id=user_id)

        device = DeviceCreation(
            user_id=user_id,
            site_id=site.id,
            name="Device",
            model="Model",
            type="Type",
            description="Description",
        )
        device = crud.create_device(db=db, device_input=device)

        return {"device_id": device.id, "site_id": site.id, "user_id": user_id}

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
    
    def test_update_device_site_id(
            self, client: TestClient, db,
            devicesbatch, normal_token_headers: dict) -> None:
        
        device_id = devicesbatch["device_id"]
        #Create a new site
        site = SiteCreation(name="Site", description="Description")
        new_site = crud.create_site(db=db, site_input=site, user_id=devicesbatch["user_id"])
               
        device = {
            "site_id": new_site.id,
        }
        response = client.patch(f"/devices/{device_id}", headers=normal_token_headers, json=device)

        assert response.status_code == 200
        assert response.json()["site_id"] == new_site.id

    def test_update_device_wrong_site_id(
            self, client: TestClient,
            devicesbatch, normal_token_headers: dict) -> None:
        
        device_id = devicesbatch["device_id"]
        device = {
            "site_id": 999,
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
        s = SiteCreation(name="Site", description="Description")
        site = crud.create_site(db=db, site_input=s, user_id=user.id)

        d = DeviceCreation(
            user_id=user.id, # <<< user ID from different user to be use in the request
            site_id=site.id,
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

        site = SiteCreation(name="Site", description="Description")
        site = crud.create_site(db=db, site_input=site, user_id=user_id)

        device = DeviceCreation(
                user_id=user_id,
                site_id=site.id,
                name="Device",
                model="Model",
                type="Type",
                description="Description",
            )
        device = crud.create_device(db=db, device_input=device)

        return {"site_id": site.id, "user_id": user_id, "device_id": device.id}

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
        s = SiteCreation(name="Site", description="Description")
        site = crud.create_site(db=db, site_input=s, user_id=user.id)

        d = DeviceCreation(
            user_id=user.id, # <<< user ID from different user to be use in the request
            site_id=site.id,
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

        site = SiteCreation(name="Site", description="Description")
        site = crud.create_site(db=db, site_input=site, user_id=user_id)

        rng = 10
        for i in range(rng):
            device = DeviceCreation(
                user_id=user_id,
                site_id=site.id,
                name=f"Device_{i}",
                model=f"Model{i}",
                type="Type",
                description="Description",
            )
            crud.create_device(db=db, device_input=device)

        return {"range": rng, "site_id": site.id, "user_id": user_id}

    def test_delete_all_devices(
            self, client: TestClient, db: Session,
            devicesbatch, normal_token_headers: dict) -> None:

        site_id = devicesbatch["site_id"]

        response = client.delete(f"/devices/site/{site_id}", headers=normal_token_headers)
        assert response.status_code == 200

        statement = select(Device).where(Device.site_id == site_id)
        results = db.exec(statement)
        assert not results.all()

    def test_delete_all_devices_no_token(self, client: TestClient) -> None:
        response = client.delete("/devices/site/1")
        assert response.status_code == 401

    def test_delete_all_devices_not_found(
            self, client: TestClient, normal_token_headers: dict) -> None:
        response = client.delete("/devices/site/999", headers=normal_token_headers)
        assert response.status_code == 404

    def test_delete_all_devices_wrong_user(
            self,
            db: Session, client: TestClient,
            normal_token_headers: dict) -> None:

        u = UserCreation(email="email", username="random_lower_string()", password="random_lower_string()")
        user = crud.create_user(db=db, user_input=u)
        s = SiteCreation(name="Site", description="Description")
        site = crud.create_site(db=db, site_input=s, user_id=user.id)

        d = DeviceCreation(
            user_id=user.id,
            site_id=site.id, # <<< user ID from different user to be use in the request
            name="Device",
            model="Model",
            type="Type",
            description="Description",
        )
        crud.create_device(db=db, device_input=d)

        response = client.delete(f"/devices/site/{site.id}", headers=normal_token_headers)
        assert response.status_code == 403
