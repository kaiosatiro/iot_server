import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

import src.crud as crud
from src.core.config import settings
from src.models import SiteCreate


class TestGetSites:
    def test_get_sites_superuser(
            self,
            client: TestClient,
            superuser_token_headers: dict,
            db: Session
    ) -> None:
        site = SiteCreate(name="test")
        crud.site.create(db, obj_in=site)
        response = client.get(f"/sites/", headers=superuser_token_headers)
        assert response.status_code == 200
        assert response.json()["data"][0]["name"] == "test"