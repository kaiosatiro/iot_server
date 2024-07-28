import pytest
from fastapi.testclient import TestClient

import src.crud as crud
from src.models import (
    SiteCreation,
)


class TestGetSites:
    @pytest.fixture(name="sitesbatchrange", autouse=True, scope="class")
    def sitesbatch(self, db, client: TestClient, normal_token_headers) -> tuple[int, int]:
        response = client.get("/users/me", headers=normal_token_headers)
        user_id = response.json()["id"]
        rng = 10
        for _ in range(rng):
            site = SiteCreation(name=f"Site_{_}")
            crud.create_site(db=db, site_input=site, user_id=user_id)
        return rng

    def test_get_sites(
            self,
            client: TestClient,
            normal_token_headers: dict,
            sitesbatchrange
    ) -> None:

        response = client.get("/sites/", headers=normal_token_headers)

        assert response.status_code == 200
        assert response.json()["count"] == sitesbatchrange, "Should be the count define in the fixture"
        assert response.json()["data"], "Should return a list of sites"

    def test_get_sites_no_token(self, client: TestClient) -> None:
        response = client.get("/sites/")
        assert response.status_code == 401

    def test_get_sites_no_sites(self, client: TestClient, superuser_token_headers: dict) -> None:
        response = client.get("/sites/", headers=superuser_token_headers)
        assert response.status_code == 200
        assert response.json()["count"] == 0, "Should be 0"


class TestCreateSite:
    def test_create_site(
            self,
            client: TestClient,
            normal_token_headers: dict,
    ) -> None:
        site = SiteCreation(name="Site_1")
        response = client.post("/sites/", headers=normal_token_headers, json=site.model_dump())

        assert response.status_code == 201
        assert response.json()["name"] == site.name

    def test_create_site_no_token(self, client: TestClient) -> None:
        site = SiteCreation(name="Site_1")
        response = client.post("/sites/", json=site.model_dump())

        assert response.status_code == 401

    def test_create_site_no_name(self, client: TestClient, normal_token_headers: dict) -> None:
        response = client.post("/sites/", headers=normal_token_headers, json={})

        assert response.status_code == 422

    def test_create_site_no_site(self, client: TestClient, normal_token_headers: dict) -> None:
        response = client.post("/sites/", headers=normal_token_headers)

        assert response.status_code == 422


class TestPatchSite:
    @pytest.fixture(name="site_id", autouse=True, scope="class")
    def site_id(self, client: TestClient, normal_token_headers) -> int:
        site = SiteCreation(name="Site_1")
        response = client.post("/sites/", headers=normal_token_headers, json=site.model_dump())
        return response.json()["id"]

    def test_patch_site(
            self,
            client: TestClient,
            normal_token_headers: dict,
            site_id: int
    ) -> None:
        site = SiteCreation(name="Site_2")
        response = client.patch(f"/sites/{site_id}", headers=normal_token_headers, json=site.model_dump())

        assert response.status_code == 200
        assert response.json()["name"] == site.name

    def test_patch_site_no_token(self, client: TestClient, site_id: int) -> None:
        site = SiteCreation(name="Site_2")
        response = client.patch(f"/sites/{site_id}", json=site.model_dump())

        assert response.status_code == 401

    @pytest.mark.skip("Not implemented")
    def test_patch_site_no_name(self, client: TestClient, normal_token_headers: dict, site_id: int) -> None:
        response = client.patch(f"/sites/{site_id}", headers=normal_token_headers, json={})

        assert response.status_code == 422

    def test_patch_site_no_site(self, client: TestClient, normal_token_headers: dict, site_id: int) -> None:
        response = client.patch(f"/sites/{site_id}", headers=normal_token_headers)

        assert response.status_code == 422


class TestDeleteSite:
    @pytest.fixture(name="site_id", autouse=True, scope="class")
    def site_id(self, client: TestClient, normal_token_headers) -> int:
        site = SiteCreation(name="Site_1")
        response = client.post("/sites/", headers=normal_token_headers, json=site.model_dump())
        return response.json()["id"]

    def test_delete_site(
            self,
            client: TestClient,
            normal_token_headers: dict,
            site_id: int
    ) -> None:
        response = client.delete(f"/sites/{site_id}", headers=normal_token_headers)

        assert response.status_code == 200

    def test_delete_site_no_token(self, client: TestClient, site_id: int) -> None:
        response = client.delete(f"/sites/{site_id}")

        assert response.status_code == 401

    def test_delete_site_no_site(self, client: TestClient, normal_token_headers: dict) -> None:
        response = client.delete("/sites/", headers=normal_token_headers)

        assert response.status_code == 405
