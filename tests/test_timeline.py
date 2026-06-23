from fastapi.testclient import TestClient


def test_timeline_all(client: TestClient, auth_header: dict):
    # Arrange
    client.post("/api/v1/posts", json={"content": "投稿1"}, headers=auth_header)
    client.post("/api/v1/posts", json={"content": "投稿2"}, headers=auth_header)

    # Act
    response = client.get("/api/v1/timeline?filter=all", headers=auth_header)

    # Assert
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 2
    assert data[0]["content"] == "投稿2"  # 新着順


def test_timeline_following(client: TestClient, auth_header: dict, second_user: dict, second_auth_header: dict):
    # Arrange
    client.post("/api/v1/posts", json={"content": "user2の投稿"}, headers=second_auth_header)
    client.post("/api/v1/users/user2/follow", headers=auth_header)

    # Act
    response = client.get("/api/v1/timeline?filter=following", headers=auth_header)

    # Assert
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) >= 1
    assert any(p["username"] == "user2" for p in data)


def test_timeline_pagination(client: TestClient, auth_header: dict):
    # Arrange
    for i in range(10):
        client.post("/api/v1/posts", json={"content": f"投稿{i}"}, headers=auth_header)

    # Act
    response = client.get("/api/v1/timeline?limit=5&offset=0", headers=auth_header)

    # Assert
    assert response.status_code == 200
    assert len(response.json()["data"]) == 5


def test_timeline_no_auth(client: TestClient):
    # Act
    response = client.get("/api/v1/timeline")

    # Assert
    assert response.status_code == 403
