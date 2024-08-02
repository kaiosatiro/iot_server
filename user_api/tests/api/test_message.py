from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

import src.crud as crud
from src.models import (
    DeviceCreation,
    Message,
    MessageCreation,
    SiteCreation,
    UserCreation,
)


class TestGetMessages:
    @pytest.fixture()
    def batch(self, db: Session, client: TestClient, normal_token_headers) -> tuple[int, int]:
        response = client.get("/users/me", headers=normal_token_headers)
        user_id = response.json()["id"]

        site = SiteCreation(name="Site", description="Description")
        site = crud.create_site(db=db, site_input=site, user_id=user_id)

        device = DeviceCreation(
                user_id=user_id, site_id=site.id,
                name="Device", model="Model",
                type="Type", description="Description")

        device = crud.create_device(db=db, device_input=device)

        messages = []
        range_number = 100
        for _ in range(range_number):
            message = MessageCreation(
                message={"Message": "Message"},
                device_id=device.id,
            )
            message_in = Message.model_validate(message)
            messages.append(message_in)

        db.add_all(messages)
        db.commit()

        return {
            "site_id": site.id,
            "user_id": user_id,
            "device_id": device.id,
            "device_name": device.name,
            "range": range_number
        }

    def test_get_messages_by_device_id(
            self, client: TestClient,
            normal_token_headers, batch
    ) -> None:

        response = client.get(f"/messages/device/{batch['device_id']}", headers=normal_token_headers)

        assert response.status_code == 200
        assert response.json()["count"] == batch["range"], "Set in the fixture"
        assert response.json()["device_name"] == batch["device_name"]
        assert response.json()["device_id"] == batch["device_id"]
        assert response.json()["data"], "Messages are expected"

    def test_get_messages_by_device_id_not_found(
            self,
            client: TestClient,
            normal_token_headers
    ) -> None:
        response = client.get("/messages/device/0", headers=normal_token_headers)
        assert response.status_code == 404

    def test_get_messages_by_device_id_unauthorized(self, client: TestClient, batch) -> None:
        response = client.get(f"/messages/device/{batch['device_id']}")
        assert response.status_code == 401

    def test_get_messages_by_device_id_forbidden(self, client: TestClient, batch) -> None:
        response = client.get(f"/messages/device/{batch['device_id']}",
                              headers={"Authorization": "Bearer 123"})
        assert response.status_code == 403

    def test_get_messages_wrong_user(
            self,
            db: Session, client: TestClient,
            userfix, batch
    ) -> None:

        crud.create_user(db=db, user_input=UserCreation(**userfix))
        response = client.post(
            "/access-token",
            data={"username": userfix["username"], "password": userfix["password"]})
        assert response.status_code == 200
        assert response.json()["access_token"]

        token_from_different_user = response.json()["access_token"]

        device_id = batch["device_id"]
        response = client.get(f"/messages/device/{device_id}",
                              headers={"Authorization": f"Bearer {token_from_different_user}"})
        assert response.status_code == 403

    def test_get_messages_by_period(
            self,
            client: TestClient,
            normal_token_headers, batch
    ) -> None:

        from_: str = (datetime.now() - timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S"),
        to: str = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"),

        response = client.get(
            f"/messages/device/{batch['device_id']}?from_={from_[0]}&to={to[0]}",
            headers=normal_token_headers
            )
        assert response.status_code == 200
        assert response.json()["count"] == batch["range"], "Set in the fixture"

    def test_get_messages_by_period_only_date(
            self,
            client: TestClient,
            normal_token_headers, batch
    ) -> None:

        from_: str = (datetime.now() - timedelta(hours=24)).strftime("%Y-%m-%d"),
        to: str = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),

        response = client.get(
            f"/messages/device/{batch['device_id']}?from_={from_[0]}&to={to[0]}",
            headers=normal_token_headers
            )
        assert response.status_code == 200
        assert response.json()["count"] == batch["range"], "Set in the fixture"

    def test_get_messages_by_period_invalid_datetime_format(
            self,
            client: TestClient,
            normal_token_headers, batch
    ) -> None:

        from_: str = (datetime.now() - timedelta(hours=24)).strftime("%Y-%m-%d %H:%S"),
        to: str = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %M:%S"),

        response = client.get(
            f"/messages/device/{batch['device_id']}?from_={from_[0]}&to={to[0]}",
            headers=normal_token_headers
            )
        assert response.status_code == 422

    def test_get_messages_by_period_old_date(
            self,
            client: TestClient,
            normal_token_headers, batch
    ) -> None:

        from_: str = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"),
        to: str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),

        response = client.get(
            f"/messages/device/{batch['device_id']}?from_={from_[0]}&to={to[0]}",
            headers=normal_token_headers
            )
        assert response.status_code == 200
        assert response.json()["count"] == 0, "No messages in the period"

    def test_get_messages_by_period_with_limit(
            self,
            client: TestClient,
            normal_token_headers, batch
    ) -> None:

        response = client.get(
            f"/messages/device/{batch['device_id']}?limit=10",
            headers=normal_token_headers
            )
        assert response.status_code == 200
        assert response.json()["count"] == 10

        response = client.get(
            f"/messages/device/{batch['device_id']}?limit=33",
            headers=normal_token_headers
            )
        assert response.status_code == 200
        assert response.json()["count"] == 33

    def test_get_messages_by_period_with_offset(
            self,
            client: TestClient,
            normal_token_headers, batch
    ) -> None:

        response = client.get(
            f"/messages/device/{batch['device_id']}?offset=10",
            headers=normal_token_headers
            )
        assert response.status_code == 200
        assert response.json()["count"] == 90

        response = client.get(
            f"/messages/device/{batch['device_id']}?offset=90",
            headers=normal_token_headers
            )
        assert response.status_code == 200
        assert response.json()["count"] == 10

    def test_get_messages_by_period_with_limit_and_offset(
            self,
            client: TestClient,
            normal_token_headers, batch
    ) -> None:

        response = client.get(
            f"/messages/device/{batch['device_id']}?limit=10&offset=95",
            headers=normal_token_headers
            )
        assert response.status_code == 200
        assert response.json()["count"] == 5

        response = client.get(
            f"/messages/device/{batch['device_id']}?limit=50&offset=60",
            headers=normal_token_headers
            )
        assert response.status_code == 200
        assert response.json()["count"] == 40

    def test_get_messages_by_period_with_limit_and_offset_out_of_range(
            self,
            client: TestClient,
            normal_token_headers, batch
    ) -> None:

        response = client.get(
            f"/messages/device/{batch['device_id']}?limit=10&offset=100",
            headers=normal_token_headers
            )
        assert response.status_code == 200
        assert response.json()["count"] == 0

    def test_get_messages_by_period_with_limit_and_offset_and_date(
            self,
            client: TestClient,
            normal_token_headers, batch
    ) -> None:

        from_: str = (datetime.now() - timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S"),
        to: str = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"),

        response = client.get(
            f"/messages/device/{batch['device_id']}?from_={from_[0]}&to={to[0]}&limit=10&offset=90",
            headers=normal_token_headers
            )
        assert response.status_code == 200
        assert response.json()["count"] == 10

        response = client.get(
            f"/messages/device/{batch['device_id']}?from_={from_[0]}&to={to[0]}&limit=50&offset=60",
            headers=normal_token_headers
            )
        assert response.status_code == 200
        assert response.json()["count"] == 40

    @pytest.mark.skip(reason="Not implemented")
    def test_get_messages_messages_create_on_order(
            self,
            client: TestClient,
            normal_token_headers, batch
    ) -> None:

        response = client.get(
            f"/messages/device/{batch['device_id']}",
            headers=normal_token_headers
            )
        assert response.status_code == 200


class TestDeleteMessage:
    @pytest.fixture()
    def batch(self, db: Session, client: TestClient, normal_token_headers) -> tuple[int, int]:
        response = client.get("/users/me", headers=normal_token_headers)
        user_id = response.json()["id"]

        site = SiteCreation(name="Site", description="Description")
        site = crud.create_site(db=db, site_input=site, user_id=user_id)

        device = DeviceCreation(
                user_id=user_id, site_id=site.id,
                name="Device", model="Model",
                type="Type", description="Description")

        device = crud.create_device(db=db, device_input=device)

        messages = []
        range_number = 10
        for _ in range(range_number):
            message = MessageCreation(
                message={"Message": "Message"},
                device_id=device.id,
            )
            message_in = Message.model_validate(message)
            messages.append(message_in)

        db.add_all(messages)
        db.commit()

        return {"site_id": site.id, "user_id": user_id, "device_id": device.id, "range": range_number}

    def test_delete_message_per_message_id(
            self, db: Session, client: TestClient,
            normal_token_headers, batch
    ) -> None:

        response = client.get(f"/messages/device/{batch['device_id']}", headers=normal_token_headers)

        assert response.status_code == 200
        assert response.json()["count"] == batch["range"], "Set in the fixture"

        message_id = response.json()["data"][0]["id"]
        assert message_id

        response = client.delete(f"/messages/{message_id}", headers=normal_token_headers)
        assert response.status_code == 200

        assert not crud.get_message_by_id(db=db, message_id=message_id)

    def test_delete_message_per_message_id_not_found(
            self,
            client: TestClient,
            normal_token_headers
    ) -> None:
        response = client.delete("/messages/999", headers=normal_token_headers)
        assert response.status_code == 404

    def test_delete_message_per_message_id_unauthorized(self, client: TestClient, batch) -> None:
        response = client.delete(f"/messages/{batch['device_id']}")
        assert response.status_code == 401

    def test_delete_message_per_id_wrong_user(
            self,
            db: Session, client: TestClient,
            userfix, batch, normal_token_headers
    ) -> None:

        # Get a message ID
        response = client.get(f"/messages/device/{batch['device_id']}", headers=normal_token_headers)
        assert response.status_code == 200
        assert response.json()["count"] == batch["range"], "Set in the fixture"
        message_id = response.json()["data"][0]["id"]
        assert message_id

        # Create a different user
        crud.create_user(db=db, user_input=UserCreation(**userfix))
        response = client.post(
            "/access-token",
            data={"username": userfix["username"], "password": userfix["password"]})
        assert response.status_code == 200
        assert response.json()["access_token"]

        # Try to delete a message from a different user
        token_from_different_user = response.json()["access_token"]
        response = client.delete(f"/messages/{message_id}",
                                 headers={"Authorization": f"Bearer {token_from_different_user}"})
        assert response.status_code == 403


class TestDeleteMessages:
    @pytest.fixture()
    def batch(self, db: Session, client: TestClient, normal_token_headers) -> tuple[int, int]:
        response = client.get("/users/me", headers=normal_token_headers)
        user_id = response.json()["id"]

        site = SiteCreation(name="Site", description="Description")
        site = crud.create_site(db=db, site_input=site, user_id=user_id)

        device = DeviceCreation(
                user_id=user_id, site_id=site.id,
                name="Device", model="Model",
                type="Type", description="Description")

        device = crud.create_device(db=db, device_input=device)

        messages = []
        range_number = 100
        for _ in range(range_number):
            message = MessageCreation(
                message={"Message": "Message"},
                device_id=device.id,
            )
            message_in = Message.model_validate(message)
            messages.append(message_in)

        db.add_all(messages)
        db.commit()

        return {"site_id": site.id, "user_id": user_id, "device_id": device.id, "range": range_number}

    def test_delete_messages_per_device_id(
            self, client: TestClient,
            normal_token_headers, batch
    ) -> None:

        response = client.delete(
            f"/messages/device/{batch['device_id']}", headers=normal_token_headers)
        assert response.status_code == 200

        response = client.get(f"/messages/device/{batch['device_id']}", headers=normal_token_headers)
        assert response.status_code == 200
        assert response.json()["count"] == 0

    def test_delete_messages_per_device_id_not_found(
            self,
            client: TestClient,
            normal_token_headers
    ) -> None:
        response = client.delete("/messages/device/999", headers=normal_token_headers)
        assert response.status_code == 404

    def test_delete_messages_per_device_id_unauthorized(self, client: TestClient, batch) -> None:
        response = client.delete(f"/messages/device/{batch['device_id']}")
        assert response.status_code == 401

    def test_delete_messages_per_device_id_wrong_user(
            self,
            db: Session, client: TestClient,
            userfix, batch
    ) -> None:

        # Create a different user
        crud.create_user(db=db, user_input=UserCreation(**userfix))
        response = client.post(
            "/access-token",
            data={"username": userfix["username"], "password": userfix["password"]})
        assert response.status_code == 200
        assert response.json()["access_token"]

        # Try to delete a message from a different user
        token_from_different_user = response.json()["access_token"]
        response = client.delete(f"/messages/device/{batch['device_id']}",
                                 headers={"Authorization": f"Bearer {token_from_different_user}"})
        assert response.status_code == 403

    def test_delete_messages_per_device_id_with_period(
            self,
            client: TestClient,
            normal_token_headers, batch
    ) -> None:

        from_: str = (datetime.now() - timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S"),
        to: str = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"),

        response = client.delete(
            f"/messages/device/{batch['device_id']}?from_={from_[0]}&to={to[0]}",
            headers=normal_token_headers
            )
        assert response.status_code == 200

        response = client.get(f"/messages/device/{batch['device_id']}", headers=normal_token_headers)
        assert response.status_code == 200
        assert response.json()["count"] == 0

    def test_delete_messages_per_device_id_with_period_only_date(
            self,
            client: TestClient,
            normal_token_headers, batch
    ) -> None:

        from_: str = (datetime.now() - timedelta(hours=24)).strftime("%Y-%m-%d"),
        to: str = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),

        response = client.delete(
            f"/messages/device/{batch['device_id']}?from_={from_[0]}&to={to[0]}",
            headers=normal_token_headers
            )
        assert response.status_code == 200

        response = client.get(f"/messages/device/{batch['device_id']}", headers=normal_token_headers)
        assert response.status_code == 200
        assert response.json()["count"] == 0

    def test_delete_messages_per_device_id_with_period_invalid_datetime_format(
            self,
            client: TestClient,
            normal_token_headers, batch
    ) -> None:

        from_: str = (datetime.now() - timedelta(hours=24)).strftime("%Y-%m-%d %H:%S"),
        to: str = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %M:%S"),

        response = client.delete(
            f"/messages/device/{batch['device_id']}?from_={from_[0]}&to={to[0]}",
            headers=normal_token_headers
            )
        assert response.status_code == 422

    def test_delete_messages_per_device_id_with_period_old_date(
            self,
            client: TestClient,
            normal_token_headers, batch
    ) -> None:

        from_: str = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"),
        to: str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),

        response = client.delete(
            f"/messages/device/{batch['device_id']}?from_={from_[0]}&to={to[0]}",
            headers=normal_token_headers
            )
        assert response.status_code == 200

        response = client.get(f"/messages/device/{batch['device_id']}", headers=normal_token_headers)
        assert response.status_code == 200
        assert response.json()["count"] == 100

    def test_delete_all_messages_per_device_id(
            self,
            client: TestClient,
            normal_token_headers, batch
    ) -> None:

        response = client.delete(
            f"/messages/device/{batch['device_id']}?all=True",
            headers=normal_token_headers
            )
        assert response.status_code == 200

        response = client.get(f"/messages/device/{batch['device_id']}", headers=normal_token_headers)
        assert response.status_code == 200
        assert response.json()["count"] == 0


class TestGetMessage:
    @pytest.fixture()
    def batch(self, db: Session, client: TestClient, normal_token_headers) -> tuple[int, int]:
        response = client.get("/users/me", headers=normal_token_headers)
        user_id = response.json()["id"]

        site = SiteCreation(name="Site", description="Description")
        site = crud.create_site(db=db, site_input=site, user_id=user_id)

        device = DeviceCreation(
                user_id=user_id, site_id=site.id,
                name="Device", model="Model",
                type="Type", description="Description")

        device = crud.create_device(db=db, device_input=device)

        messages = []
        range_number = 10
        for _ in range(range_number):
            message = MessageCreation(
                message={"Message": "Message"},
                device_id=device.id,
            )
            message_in = Message.model_validate(message)
            messages.append(message_in)

        db.add_all(messages)
        db.commit()

        messages = crud.get_messages(db=db, device_id=device.id)
        message_id = messages[0].id

        return message_id

    def test_get_message_by_id(
            self, client: TestClient,
            normal_token_headers, batch
    ) -> None:

        response = client.get(f"/messages/{batch}", headers=normal_token_headers)
        assert response.status_code == 200
        assert response.json()["id"] == batch

    def test_get_message_by_id_not_found(
            self,
            client: TestClient,
            normal_token_headers
    ) -> None:
        response = client.get("/messages/999", headers=normal_token_headers)
        assert response.status_code == 404

    def test_get_message_by_id_unauthorized(self, client: TestClient, batch) -> None:
        response = client.get(f"/messages/{batch}")
        assert response.status_code == 401

    def test_get_message_by_id_wrong_user(
            self,
            db: Session, client: TestClient,
            userfix, batch
    ) -> None:

        # Create a different user
        crud.create_user(db=db, user_input=UserCreation(**userfix))
        response = client.post(
            "/access-token",
            data={"username": userfix["username"], "password": userfix["password"]})
        assert response.status_code == 200
        assert response.json()["access_token"]

        # Try to delete a message from a different user
        token_from_different_user = response.json()["access_token"]
        response = client.get(f"/messages/{batch}",
                              headers={"Authorization": f"Bearer {token_from_different_user}"})
        assert response.status_code == 403
