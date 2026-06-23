from fastapi.testclient import TestClient


def test_follow(client: TestClient, auth_header: dict, second_user: dict):
    # Act
    response = client.post("/api/v1/users/user2/follow", headers=auth_header)

    # Assert
    assert response.status_code == 201
    assert response.json()["data"]["message"] == "フォローしました"


def test_follow_self(client: TestClient, auth_header: dict, registered_user: dict):
    # Act
    response = client.post("/api/v1/users/testuser/follow", headers=auth_header)

    # Assert
    assert response.status_code == 400


def test_follow_already_following(client: TestClient, auth_header: dict, second_user: dict):
    # Arrange
    client.post("/api/v1/users/user2/follow", headers=auth_header)

    # Act
    response = client.post("/api/v1/users/user2/follow", headers=auth_header)

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "ALREADY_FOLLOWING"


def test_unfollow(client: TestClient, auth_header: dict, second_user: dict):
    # Arrange
    client.post("/api/v1/users/user2/follow", headers=auth_header)

    # Act
    response = client.delete("/api/v1/users/user2/follow", headers=auth_header)

    # Assert
    assert response.status_code == 200
    assert response.json()["data"]["message"] == "フォローを解除しました"


def test_unfollow_not_following(client: TestClient, auth_header: dict, second_user: dict):
    # Act
    response = client.delete("/api/v1/users/user2/follow", headers=auth_header)

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "NOT_FOLLOWING"


def test_get_followers(client: TestClient, auth_header: dict, second_user: dict, second_auth_header: dict):
    # Arrange
    client.post("/api/v1/users/testuser/follow", headers=second_auth_header)

    # Act
    response = client.get("/api/v1/users/testuser/followers", headers=auth_header)

    # Assert
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 1
    assert data[0]["username"] == "user2"


def test_get_following(client: TestClient, auth_header: dict, second_user: dict):
    # Arrange
    client.post("/api/v1/users/user2/follow", headers=auth_header)

    # Act
    response = client.get("/api/v1/users/testuser/following", headers=auth_header)

    # Assert
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 1
    assert data[0]["username"] == "user2"
