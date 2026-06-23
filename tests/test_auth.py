import pytest
from fastapi.testclient import TestClient


def test_register_success(client: TestClient):
    # Arrange
    payload = {
        "username": "newuser",
        "email": "new@example.com",
        "password": "password123",
        "display_name": "新規ユーザ",
    }

    # Act
    response = client.post("/api/v1/auth/register", json=payload)

    # Assert
    assert response.status_code == 201
    data = response.json()["data"]
    assert "token" in data
    assert data["user"]["username"] == "newuser"
    assert data["user"]["email"] == "new@example.com"


def test_register_duplicate_username(client: TestClient, registered_user: dict):
    # Arrange
    payload = {
        "username": "testuser",
        "email": "other@example.com",
        "password": "password123",
    }

    # Act
    response = client.post("/api/v1/auth/register", json=payload)

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "USERNAME_EXISTS"


def test_register_duplicate_email(client: TestClient, registered_user: dict):
    # Arrange
    payload = {
        "username": "otheruser",
        "email": "test@example.com",
        "password": "password123",
    }

    # Act
    response = client.post("/api/v1/auth/register", json=payload)

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "EMAIL_EXISTS"


@pytest.mark.parametrize(
    "username",
    ["ab", "a" * 21, "user!name", "user name"],
)
def test_register_invalid_username(client: TestClient, username: str):
    # Arrange
    payload = {
        "username": username,
        "email": "valid@example.com",
        "password": "password123",
    }

    # Act
    response = client.post("/api/v1/auth/register", json=payload)

    # Assert
    assert response.status_code == 422


def test_register_short_password(client: TestClient):
    # Arrange
    payload = {
        "username": "validuser",
        "email": "valid@example.com",
        "password": "short",
    }

    # Act
    response = client.post("/api/v1/auth/register", json=payload)

    # Assert
    assert response.status_code == 422


def test_login_success(client: TestClient, registered_user: dict):
    # Arrange
    payload = {
        "email": "test@example.com",
        "password": "password123",
    }

    # Act
    response = client.post("/api/v1/auth/login", json=payload)

    # Assert
    assert response.status_code == 200
    data = response.json()["data"]
    assert "token" in data
    assert data["user"]["username"] == "testuser"


def test_login_wrong_email(client: TestClient):
    # Arrange
    payload = {
        "email": "nonexistent@example.com",
        "password": "password123",
    }

    # Act
    response = client.post("/api/v1/auth/login", json=payload)

    # Assert
    assert response.status_code == 401


def test_login_wrong_password(client: TestClient, registered_user: dict):
    # Arrange
    payload = {
        "email": "test@example.com",
        "password": "wrongpassword",
    }

    # Act
    response = client.post("/api/v1/auth/login", json=payload)

    # Assert
    assert response.status_code == 401


def test_me_success(client: TestClient, auth_header: dict):
    # Act
    response = client.get("/api/v1/auth/me", headers=auth_header)

    # Assert
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["username"] == "testuser"
    assert "created_at" in data


def test_me_no_token(client: TestClient):
    # Act
    response = client.get("/api/v1/auth/me")

    # Assert
    assert response.status_code == 403


def test_me_invalid_token(client: TestClient):
    # Act
    response = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid"})

    # Assert
    assert response.status_code == 401
