from fastapi.testclient import TestClient
from sqlmodel import Session

import src.core.security as security
import src.crud as crud
from src.core.config import settings
from src.models import UserCreation


class TestGetAccessToken:
    def test_get_access_token(self, client: TestClient) -> None:
        login_data = {
            "username": settings.FIRST_SUPERUSERNAME,
            "password": settings.FIRST_SUPERUSER_PASSWORD,
        }
        response = client.post("/access-token", data=login_data)
        tokens = response.json()
        assert response.status_code == 200
        assert "access_token" in tokens
        assert tokens["access_token"]

    def test_get_access_token_incorrect_password(self, client: TestClient) -> None:
        login_data = {
            "username": settings.FIRST_SUPERUSERNAME,
            "password": "incorrect",
        }
        response = client.post("/access-token", data=login_data)
        assert response.status_code == 401
        assert response.json()["detail"] == "Incorrect username or password"

    def test_get_access_token_inactive_user(
        self, db: Session, client: TestClient, userfix: dict
    ) -> None:
        user_in = UserCreation(**userfix)
        user = crud.create_user(db=db, user_input=user_in)
        login_data = {
            "username": user_in.username,
            "password": user_in.password,
        }
        response = client.post("/access-token", data=login_data)
        assert response.status_code == 200

        user_in = crud.deactivate_user(db=db, user=user)
        assert not user_in.is_active

        # Test inactive user
        response = client.post("/access-token", data=login_data)
        assert response.status_code == 401
        assert response.json()["detail"] == "Inactive user"


class TestTestToken:
    def test_test_token(self, client: TestClient, superuser_token_headers) -> None:
        response = client.post("/login/test-token", headers=superuser_token_headers)
        assert response.status_code == 200
        assert response.json()["username"] == settings.FIRST_SUPERUSERNAME

    def test_test_token_invalid(self, client: TestClient) -> None:
        response = client.post("/login/test-token")
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"


class TestPasswordRecovery:
    def test_password_recovery(
            self, client: TestClient,
            normaluser_fixture: dict,
            ) -> None:

        email = normaluser_fixture["email"]

        response = client.post(f"/password-recovery/{email}")
        assert response.status_code == 200

    def test_password_recovery_invalid_email(
            self, client: TestClient,
            ) -> None:

        email = "mail@mail.com"

        response = client.post(f"/password-recovery/{email}")
        assert response.status_code == 404


class TestResetPassword:
    def test_reset_password(
            self, client: TestClient, db: Session,
            normaluser_fixture: dict,
            ) -> None:

        email = normaluser_fixture["email"]

        password_reset_token = security.generate_password_reset_token(email=email)
        new_password = "newpassword"
        data = {
            "token": password_reset_token,
            "new_password": new_password,
        }

        response = client.post("/reset-password", json=data)
        import logging
        logging.error(response.json())
        assert response.status_code == 200

        user = crud.get_user_by_email(db=db, email=email)
        assert security.verify_password(new_password, user.hashed_password)

    def test_reset_password_invalid_token(
            self, client: TestClient,
            ) -> None:

        new_password = "newpassword"
        data = {
            "token": "invalidtoken",
            "new_password": new_password,
        }

        response = client.post("/reset-password", json=data)
        assert response.status_code == 400
