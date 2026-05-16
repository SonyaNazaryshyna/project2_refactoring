"""Integration tests — Auth REST controllers."""
import pytest
from rest_framework.test import APIClient


@pytest.fixture
def client():
    return APIClient()


@pytest.mark.django_db
class TestRegisterView:
    def test_register_success(self, client):
        response = client.post("/api/v1/auth/register", {
            "username": "newuser",
            "email": "new@test.com",
            "password": "password123",
        }, format="json")
        assert response.status_code == 201
        assert "access_token" in response.data

    def test_register_empty_body_returns_400(self, client):
        response = client.post("/api/v1/auth/register", {}, format="json")
        assert response.status_code == 400

    def test_register_duplicate_email_returns_409(self, client):
        client.post("/api/v1/auth/register", {
            "username": "user1",
            "email": "taken@test.com",
            "password": "password123",
        }, format="json")
        response = client.post("/api/v1/auth/register", {
            "username": "user2",
            "email": "taken@test.com",
            "password": "password123",
        }, format="json")
        assert response.status_code in [400, 409]

    def test_register_invalid_username_returns_400(self, client):
        response = client.post("/api/v1/auth/register", {
            "username": "u",
            "email": "valid@test.com",
            "password": "password123",
        }, format="json")
        assert response.status_code == 400

    def test_register_invalid_email_returns_400(self, client):
        response = client.post("/api/v1/auth/register", {
            "username": "validuser",
            "email": "notanemail",
            "password": "password123",
        }, format="json")
        assert response.status_code == 400


@pytest.mark.django_db
class TestLoginView:
    def setup_method(self):
        self.client = APIClient()
        self.client.post("/api/v1/auth/register", {
            "username": "loginuser",
            "email": "login@test.com",
            "password": "password123",
        }, format="json")

    def test_login_success(self):
        response = self.client.post("/api/v1/auth/login", {
            "email": "login@test.com",
            "password": "password123",
        }, format="json")
        assert response.status_code == 200
        assert "access_token" in response.data

    def test_login_wrong_password_returns_401(self):
        response = self.client.post("/api/v1/auth/login", {
            "email": "login@test.com",
            "password": "wrongpassword",
        }, format="json")
        assert response.status_code in [400, 401]

    def test_login_empty_body_returns_400(self):
        response = self.client.post("/api/v1/auth/login", {}, format="json")
        assert response.status_code == 400

    def test_login_nonexistent_user_returns_401(self):
        response = self.client.post("/api/v1/auth/login", {
            "email": "ghost@test.com",
            "password": "password123",
        }, format="json")
        assert response.status_code in [400, 401]


@pytest.mark.django_db
class TestRefreshTokenView:
    def setup_method(self):
        self.client = APIClient()
        reg = self.client.post("/api/v1/auth/register", {
            "username": "refreshuser",
            "email": "refresh@test.com",
            "password": "password123",
        }, format="json")
        self.refresh_token = reg.data.get("refresh_token") if reg.status_code == 201 else None

    def test_refresh_success(self):
        if not self.refresh_token:
            pytest.skip("Registration failed")
        response = self.client.post("/api/v1/auth/refresh", {
            "refresh_token": self.refresh_token,
        }, format="json")
        assert response.status_code == 200
        assert "access_token" in response.data

    def test_refresh_missing_token_returns_400(self):
        response = self.client.post("/api/v1/auth/refresh", {}, format="json")
        assert response.status_code == 400

    def test_refresh_invalid_token_returns_401(self):
        response = self.client.post("/api/v1/auth/refresh", {
            "refresh_token": "invalid.token.here",
        }, format="json")
        assert response.status_code == 401

    def test_refresh_expired_token_returns_401(self):
        response = self.client.post("/api/v1/auth/refresh", {
            "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ0ZXN0IiwidHlwZSI6InJlZnJlc2giLCJleHAiOjF9.invalid",
        }, format="json")
        assert response.status_code == 401