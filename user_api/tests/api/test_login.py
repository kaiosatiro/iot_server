from fastapi.testclient import TestClient
from sqlmodel import Session

from src.core.config import settings
import src.crud as crud
from src.models import UserCreate


def test_get_access_token(client: TestClient) -> None:
    login_data = {
        "username": settings.FIRST_SUPERUSERNAME,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    response = client.post(f"/access-token", data=login_data)
    tokens = response.json()
    assert response.status_code == 200
    assert "access_token" in tokens
    assert tokens["access_token"]


def test_get_access_token_incorrect_password(client: TestClient) -> None:
    login_data = {
        "username": settings.FIRST_SUPERUSERNAME,
        "password": "incorrect",
    }
    response = client.post(f"/access-token", data=login_data)
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


def test_get_access_token_inactive_user(db: Session, client: TestClient, userfix: dict) -> None:
    user_in = UserCreate(**userfix)
    user = crud.create_user(db=db, user_input=user_in)
    login_data = {
        "username": user_in.username,
        "password": user_in.password,
    }
    response = client.post(f"/access-token", data=login_data)
    assert response.status_code == 200

    user_in = crud.deactivate_user(db=db, user=user)
    assert not user_in.is_active

    # Test inactive user
    response = client.post(f"/access-token", data=login_data)
    assert response.status_code == 401
    assert response.json()["detail"] == "Inactive user"
    


