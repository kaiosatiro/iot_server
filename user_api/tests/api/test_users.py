import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

import src.crud as crud
from src.core.config import settings
from src.models import UserCreate
from tests.utils import random_email, random_lower_string


class TestGetUsers:
    def test_get_users_superuser(
        self, client: TestClient, superuser_token_headers: dict[str, str]
    ) -> None:
        response = client.get("/users", headers=superuser_token_headers)
        response_data = response.json()

        assert response.status_code == 200
        assert response_data["count"] == 1
        assert response_data["data"][0]["email"] == settings.FIRST_SUPERUSER_EMAIL

    def test_get_users_superuser_no_superuser(
        self, client: TestClient, normal_token_headers: dict[str, str]
    ) -> None:
        response = client.get("/users", headers=normal_token_headers)

        assert response.status_code == 403
        assert response.json() == {"detail": "Not enough privileges"}

    def test_get_users_superuser_no_token(self, client: TestClient) -> None:
        response = client.get("/users")
        assert response.status_code == 401
        assert response.json() == {"detail": "Not authenticated"}

    def test_get_users_superuser_bad_token(self, client: TestClient) -> None:
        token = (
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
            "eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ."
            "SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        )
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get("/users", headers=headers)

        assert response.status_code == 403
        assert response.json() == {"detail": "Could not validate credentials"}

    def test_get_users_inactive_superuser(
        self, db: Session, client: TestClient, superuser_token_headers: dict[str, str]
    ) -> None:
        superuser = crud.get_user_by_username(
            db=db, username=settings.FIRST_SUPERUSERNAME
        )
        assert superuser.is_active

        superuser = crud.deactivate_user(db=db, user=superuser)
        assert not superuser.is_active

        response = client.get("/users", headers=superuser_token_headers)

        assert response.status_code == 401
        assert response.json() == {"detail": "Inactive user"}

        # superuser = crud.activate_user(db=db, user=superuser)
        # assert superuser.is_active


class TestGetMe:
    def test_get_current_user(
        self, client: TestClient, superuser_token_headers: dict[str, str]
    ) -> None:
        response = client.get("/users/me", headers=superuser_token_headers)
        response_data = response.json()

        assert response.status_code == 200
        assert response_data["email"] == settings.FIRST_SUPERUSER_EMAIL

    def test_get_current_invalid_user(self, client: TestClient) -> None:
        response = client.get("/users/me")
        assert response.status_code == 401
        assert response.json() == {"detail": "Not authenticated"}


class TestGetUser:
    def test_get_existing_user(
        self, db: Session, client: TestClient, superuser_token_headers: dict[str, str]
    ) -> None:
        username = random_lower_string()
        password = random_lower_string()
        email = random_email()
        user_in = UserCreate(username=username, email=email, password=password)
        user = crud.create_user(db=db, user_input=user_in)

        user_id = user.id
        response = client.get(f"/users/{user_id}", headers=superuser_token_headers)
        assert response.status_code == 200

        api_user = response.json()
        existing_user = crud.get_user_by_email(db=db, email=email)
        assert existing_user
        assert existing_user.email == api_user["email"]

    def test_get_non_existing_user(
        self, client: TestClient, superuser_token_headers: dict[str, str]
    ) -> None:
        response = client.get("/users/0", headers=superuser_token_headers)

        assert response.status_code == 404
        assert response.json() == {"detail": "User not found"}

    def test_get_user_no_superuser(
        self, db: Session, client: TestClient, normal_token_headers: dict[str, str]
    ) -> None:
        username = random_lower_string()
        password = random_lower_string()
        email = random_email()
        user_in = UserCreate(username=username, email=email, password=password)
        user = crud.create_user(db=db, user_input=user_in)

        user_id = user.id
        response = client.get(f"/users/{user_id}", headers=normal_token_headers)
        assert response.status_code == 403
        assert response.json() == {"detail": "Not enough privileges"}


class TestCreateUser:
    def test_create_user(
        self, client: TestClient, superuser_token_headers: dict[str, str]
    ) -> None:
        username = random_lower_string()
        password = random_lower_string()
        email = random_email()
        user_in = {"username": username, "email": email, "password": password}
        response = client.post("/users/", headers=superuser_token_headers, json=user_in)

        assert response.status_code == 201
        assert response.json()["email"] == email

    def test_create_user_no_superuser(
        self, client: TestClient, normal_token_headers: dict[str, str]
    ) -> None:
        username = random_lower_string()
        password = random_lower_string()
        email = random_email()
        user_in = {"username": username, "email": email, "password": password}
        response = client.post("/users/", headers=normal_token_headers, json=user_in)

        assert response.status_code == 403
        assert response.json() == {"detail": "Not enough privileges"}

    def test_create_user_bad_data(
        self, client: TestClient, superuser_token_headers: dict[str, str]
    ) -> None:
        username = random_lower_string()
        password = random_lower_string()
        email = random_email()
        user_in = {"username": username, "password": password}
        response = client.post("/users/", headers=superuser_token_headers, json=user_in)

        assert response.status_code == 422

        user_in = {"username": username, "email": email}
        response = client.post("/users/", headers=superuser_token_headers, json=user_in)

        assert response.status_code == 422

        user_in = {"email": email, "password": password}
        response = client.post("/users/", headers=superuser_token_headers, json=user_in)

        assert response.status_code == 422

    def test_create_user_email_exists(
        self, db: Session, client: TestClient, superuser_token_headers: dict[str, str]
    ) -> None:
        username = random_lower_string()
        password = random_lower_string()
        email = random_email()
        user_in = UserCreate(username=username, email=email, password=password)
        crud.create_user(db=db, user_input=user_in)

        user_in = {"username": username, "email": email, "password": password}
        response = client.post("/users/", headers=superuser_token_headers, json=user_in)

        assert response.status_code == 409
        assert response.json() == {
            "detail": "The user with this email already exists in the system."
        }

    def test_create_user_username_exists(
        self, db: Session, client: TestClient, superuser_token_headers: dict[str, str]
    ) -> None:
        username = random_lower_string()
        password = random_lower_string()
        email = random_email()
        user_in = UserCreate(username=username, email=email, password=password)
        crud.create_user(db=db, user_input=user_in)

        email = random_email()
        user_in = {"username": username, "email": email, "password": password}
        response = client.post("/users/", headers=superuser_token_headers, json=user_in)

        assert response.status_code == 409
        assert response.json() == {
            "detail": "The user with this username already exists in the system."
        }


class TestPatchUser:
    def test_patch_user(
        self, db: Session, client: TestClient, superuser_token_headers: dict[str, str]
    ) -> None:
        username = random_lower_string()
        password = random_lower_string()
        email = random_email()
        user_in = UserCreate(username=username, email=email, password=password)
        user = crud.create_user(db=db, user_input=user_in)

        user_id = user.id
        new_email = random_email()
        response = client.patch(
            f"/users/{user_id}",
            headers=superuser_token_headers,
            json={"email": new_email},
        )

        assert response.status_code == 200
        assert response.json()["email"] == new_email

    def test_patch_user_no_superuser(
        self, db: Session, client: TestClient, normal_token_headers: dict[str, str]
    ) -> None:
        username = random_lower_string()
        password = random_lower_string()
        email = random_email()
        user_in = UserCreate(username=username, email=email, password=password)
        user = crud.create_user(db=db, user_input=user_in)

        user_id = user.id
        new_email = random_email()
        response = client.patch(
            f"/users/{user_id}", headers=normal_token_headers, json={"email": new_email}
        )

        assert response.status_code == 403
        assert response.json() == {"detail": "Not enough privileges"}

    @pytest.mark.skip(reason="Not implemented")
    def test_patch_user_bad_data(
        self, db: Session, client: TestClient, superuser_token_headers: dict[str, str]
    ) -> None:
        username = random_lower_string()
        password = random_lower_string()
        email = random_email()
        user_in = UserCreate(username=username, email=email, password=password)
        user = crud.create_user(db=db, user_input=user_in)

        user_id = user.id
        response = client.patch(
            f"/users/{user_id}",
            headers=superuser_token_headers,
            json={"invalidfield": "invalid"},
        )

        assert response.status_code == 422

    def test_patch_user_no_user(
        self, client: TestClient, superuser_token_headers: dict[str, str]
    ) -> None:
        response = client.patch(
            "/users/0", headers=superuser_token_headers, json={"email": "test"}
        )

        assert response.status_code == 404
        assert response.json() == {"detail": "User not found"}

    def test_patch_user_ID_or_username_or_email_exist(
        self, db: Session, client: TestClient, superuser_token_headers: dict[str, str]
    ) -> None:
        password = random_lower_string()

        first_username = random_lower_string()
        first_email = random_email()
        user_in = UserCreate(
            username=first_username, email=first_email, password=password
        )
        first_user = crud.create_user(db=db, user_input=user_in)

        second_username = random_lower_string()
        second_email = random_email()
        user_in = UserCreate(
            username=second_username, email=second_email, password=password
        )
        second_user = crud.create_user(db=db, user_input=user_in)

        user_to_patch_id = first_user.id
        response = client.patch(
            f"/users/{user_to_patch_id}",
            headers=superuser_token_headers,
            json={"username": second_username},
        )
        assert response.status_code == 409
        assert response.json() == {
            "detail": "This username already exists in the system."
        }

        response = client.patch(
            f"/users/{user_to_patch_id}",
            headers=superuser_token_headers,
            json={"email": second_email},
        )
        assert response.status_code == 409
        assert response.json() == {"detail": "This email already exists in the system."}

        response = client.patch(
            f"/users/{user_to_patch_id}",
            headers=superuser_token_headers,
            json={"id": second_user.id},
        )
        assert response.status_code == 409
        assert response.json() == {"detail": "This id already exists in the system."}


class TestPatchMe:
    def test_patch_me(
        self, client: TestClient, normal_token_headers: dict[str, str]
    ) -> None:
        second_username = random_lower_string()
        second_email = random_email()

        response = client.patch(
            "/users/me",
            headers=normal_token_headers,
            json={"username": second_username},
        )
        assert response.status_code == 200
        assert response.json()["username"] == second_username

        response = client.patch(
            "/users/me", headers=normal_token_headers, json={"email": second_email}
        )
        assert response.status_code == 200
        assert response.json()["email"] == second_email

    def test_patch_me_email_exists(
        self, db: Session, client: TestClient, normal_token_headers: dict[str, str]
    ) -> None:
        password = random_lower_string()

        first_username = random_lower_string()
        first_email = random_email()
        user_in = UserCreate(
            username=first_username, email=first_email, password=password
        )
        crud.create_user(db=db, user_input=user_in)

        random_email()
        response = client.patch(
            "/users/me", headers=normal_token_headers, json={"email": first_email}
        )
        assert response.status_code == 409
        assert response.json() == {"detail": "User with this email already exists"}

    def test_patch_me_username_exists(
        self, db: Session, client: TestClient, normal_token_headers: dict[str, str]
    ) -> None:
        password = random_lower_string()

        first_username = random_lower_string()
        first_email = random_email()
        user_in = UserCreate(
            username=first_username, email=first_email, password=password
        )
        crud.create_user(db=db, user_input=user_in)

        response = client.patch(
            "/users/me", headers=normal_token_headers, json={"username": first_username}
        )
        assert response.status_code == 409
        assert response.json() == {"detail": "User with this username already exists"}


class TestPatchMePassword:
    def test_patch_me_password(
        self, client: TestClient, normaluserfix, normal_token_headers: dict[str, str]
    ) -> None:
        new_password = random_lower_string()
        response = client.patch(
            "/users/me/password",
            headers=normal_token_headers,
            json={
                "new_password": new_password,
                "current_password": normaluserfix["password"],
            },
        )
        assert response.status_code == 200
        assert response.json() == {"message": "Password updated successfully"}

    def test_patch_me_password_bad_password(
        self, client: TestClient, normaluserfix, normal_token_headers: dict[str, str]
    ) -> None:
        new_password = random_lower_string()
        response = client.patch(
            "/users/me/password",
            headers=normal_token_headers,
            json={"new_password": new_password, "current_password": "wrongpassword"},
        )
        assert response.status_code == 401
        assert response.json() == {"detail": "Incorrect password"}

    def test_patch_me_repetitive_password(
        self, client: TestClient, superuser_token_headers: dict[str, str]
    ) -> None:
        response = client.patch(
            "/users/me/password",
            headers=superuser_token_headers,
            json={
                "new_password": settings.FIRST_SUPERUSER_PASSWORD,
                "current_password": settings.FIRST_SUPERUSER_PASSWORD,
            },
        )
        assert response.status_code == 422
        assert response.json() == {
            "detail": "New password cannot be the same as the current one"
        }

    @pytest.mark.skip(reason="Not implemented")
    def test_patch_me_password_bad_data(
        self, client: TestClient, normaluserfix, normal_token_headers: dict[str, str]
    ) -> None:
        response = client.patch(
            "/users/me/password",
            headers=normal_token_headers,
            json={"new_password": "newpassword"},
        )
        assert response.status_code == 422

        response = client.patch(
            "/users/me/password",
            headers=normal_token_headers,
            json={"current_password": "password"},
        )
        assert response.status_code == 422

        response = client.patch(
            "/users/me/password", headers=normal_token_headers, json={}
        )
        assert response.status_code == 422


class TestDeactivateUserMe:
    def test_deactivate_user_me(
        self, client: TestClient, normal_token_headers: dict[str, str]
    ) -> None:
        response = client.delete("/users/me", headers=normal_token_headers)
        assert response.status_code == 200

    def test_deactivate_superuser_me(
        self, client: TestClient, superuser_token_headers: dict[str, str]
    ) -> None:
        response = client.delete("/users/me", headers=superuser_token_headers)
        assert response.status_code == 403


class TestDeactivateUser:
    def test_deactivate_user(
        self, db: Session, client: TestClient, superuser_token_headers: dict[str, str]
    ) -> None:
        username = random_lower_string()
        password = random_lower_string()
        email = random_email()
        user_in = UserCreate(username=username, email=email, password=password)
        user = crud.create_user(db=db, user_input=user_in)

        user_id = user.id
        response = client.delete(f"/users/{user_id}", headers=superuser_token_headers)
        assert response.status_code == 200

        db.refresh(user)
        assert not user.is_active

    def test_deactivate_user_no_superuser(
        self, db: Session, client: TestClient, normal_token_headers: dict[str, str]
    ) -> None:
        username = random_lower_string()
        password = random_lower_string()
        email = random_email()
        user_in = UserCreate(username=username, email=email, password=password)
        user = crud.create_user(db=db, user_input=user_in)

        user_id = user.id
        response = client.delete(f"/users/{user_id}", headers=normal_token_headers)

        assert response.status_code == 403

    def test_superuser_try_deactivate_it_self(
        self, db: Session, client: TestClient, superuser_token_headers: dict[str, str]
    ) -> None:
        superuser = crud.get_user_by_username(
            db=db, username=settings.FIRST_SUPERUSERNAME
        )
        response = client.delete(
            f"/users/{superuser.id}", headers=superuser_token_headers
        )

        assert response.status_code == 403

    def test_deactivate_user_no_user(
        self, client: TestClient, superuser_token_headers: dict[str, str]
    ) -> None:
        response = client.delete("/users/0", headers=superuser_token_headers)

        assert response.status_code == 404
        assert response.json() == {"detail": "User not found"}

    def test_deactivate_user_already_deactivated(
        self, db: Session, client: TestClient, superuser_token_headers: dict[str, str]
    ) -> None:
        username = random_lower_string()
        password = random_lower_string()
        email = random_email()
        user_in = UserCreate(username=username, email=email, password=password)
        user = crud.create_user(db=db, user_input=user_in)

        user_id = user.id
        response = client.delete(f"/users/{user_id}", headers=superuser_token_headers)
        assert response.status_code == 200

        response = client.delete(f"/users/{user_id}", headers=superuser_token_headers)
        assert response.status_code == 404
