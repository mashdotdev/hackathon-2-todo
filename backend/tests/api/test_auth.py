"""Tests for authentication endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from src.models.user import User


class TestRegister:
    """Tests for POST /api/auth/register."""

    def test_register_success(self, client: TestClient):
        """Should register a new user and return token."""
        response = client.post(
            "/api/auth/register",
            json={"email": "newuser@example.com", "password": "password123"},
        )
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "newuser@example.com"

    def test_register_duplicate_email(self, client: TestClient, test_user: User):
        """Should return 409 for duplicate email."""
        response = client.post(
            "/api/auth/register",
            json={"email": test_user.email, "password": "password123"},
        )
        assert response.status_code == 409
        assert "already registered" in response.json()["detail"].lower()

    def test_register_invalid_email(self, client: TestClient):
        """Should return 422 for invalid email format."""
        response = client.post(
            "/api/auth/register",
            json={"email": "invalid-email", "password": "password123"},
        )
        assert response.status_code == 422

    def test_register_short_password(self, client: TestClient):
        """Should return 422 for password too short."""
        response = client.post(
            "/api/auth/register",
            json={"email": "test@example.com", "password": "short"},
        )
        assert response.status_code == 422


class TestLogin:
    """Tests for POST /api/auth/login."""

    def test_login_success(self, client: TestClient, test_user: User):
        """Should login successfully with correct credentials."""
        response = client.post(
            "/api/auth/login",
            json={"email": test_user.email, "password": "testpassword123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["email"] == test_user.email

    def test_login_wrong_password(self, client: TestClient, test_user: User):
        """Should return 401 for wrong password."""
        response = client.post(
            "/api/auth/login",
            json={"email": test_user.email, "password": "wrongpassword"},
        )
        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()

    def test_login_nonexistent_user(self, client: TestClient):
        """Should return 401 for nonexistent user."""
        response = client.post(
            "/api/auth/login",
            json={"email": "nonexistent@example.com", "password": "password123"},
        )
        assert response.status_code == 401


class TestLogout:
    """Tests for POST /api/auth/logout."""

    def test_logout_success(self, client: TestClient, auth_headers: dict[str, str]):
        """Should logout successfully with valid token."""
        response = client.post("/api/auth/logout", headers=auth_headers)
        assert response.status_code == 200
        assert "logged out" in response.json()["message"].lower()

    def test_logout_no_auth(self, client: TestClient):
        """Should return 401 without authentication."""
        response = client.post("/api/auth/logout")
        assert response.status_code == 401


class TestGetCurrentUser:
    """Tests for GET /api/auth/me."""

    def test_get_current_user_success(
        self, client: TestClient, auth_headers: dict[str, str], test_user: User
    ):
        """Should return current user info."""
        response = client.get("/api/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["id"] == test_user.id

    def test_get_current_user_no_auth(self, client: TestClient):
        """Should return 401 without authentication."""
        response = client.get("/api/auth/me")
        assert response.status_code == 401
