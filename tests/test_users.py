from fastapi.testclient import TestClient


def test_get_profile(client: TestClient, auth_header: dict, registered_user: dict):
    # Act
    response = client.get("/api/v1/users/testuser", headers=auth_header)

    # Assert
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["username"] == "testuser"
    assert data["followers_count"] == 0
    assert data["following_count"] == 0


def test_get_profile_not_found(client: TestClient, auth_header: dict):
    # Act
    response = client.get("/api/v1/users/nonexistent", headers=auth_header)

    # Assert
    assert response.status_code == 404


def test_get_profile_is_following(client: TestClient, auth_header: dict, second_user: dict):
    # Arrange
    client.post("/api/v1/users/user2/follow", headers=auth_header)

    # Act
    response = client.get("/api/v1/users/user2", headers=auth_header)

    # Assert
    assert response.status_code == 200
    assert response.json()["data"]["is_following"] is True


def test_get_user_posts(client: TestClient, auth_header: dict):
    # Arrange
    client.post("/api/v1/posts", json={"content": "ユーザ投稿1"}, headers=auth_header)
    client.post("/api/v1/posts", json={"content": "ユーザ投稿2"}, headers=auth_header)

    # Act
    response = client.get("/api/v1/users/testuser/posts", headers=auth_header)

    # Assert
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 2
    assert data[0]["content"] == "ユーザ投稿2"  # 新着順
