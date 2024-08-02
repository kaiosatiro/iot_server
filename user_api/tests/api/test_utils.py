from fastapi.testclient import TestClient


class TestEmailTestRouter:
    def test_test_email(self, client: TestClient, superuser_token_headers):
        email_to = "test@mail.com"
        response = client.post(
            f"utils/test-email/?email_to={email_to}",
            headers=superuser_token_headers,
            # json={"email_to": email_to},
        )
        assert response.status_code == 201

    def test_test_email_invalid(self, client: TestClient):
        response = client.post("utils/test-email/")
        assert response.status_code == 401
        assert response.json() == {"detail": "Not authenticated"}

    def test_test_email_invalid_superuser(self, client: TestClient, normal_token_headers):
        response = client.post("utils/test-email/", headers=normal_token_headers)
        assert response.status_code == 403
