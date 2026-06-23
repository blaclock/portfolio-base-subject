from fastapi.testclient import TestClient


def test_create_post(client: TestClient, auth_header: dict):
    # Arrange
    payload = {"content": "テスト投稿です"}

    # Act
    response = client.post("/api/v1/posts", json=payload, headers=auth_header)

    # Assert
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["content"] == "テスト投稿です"
    assert data["username"] == "testuser"
    assert data["like_count"] == 0


def test_create_post_empty(client: TestClient, auth_header: dict):
    # Act
    response = client.post("/api/v1/posts", json={"content": ""}, headers=auth_header)

    # Assert
    assert response.status_code == 422


def test_create_post_too_long(client: TestClient, auth_header: dict):
    # Arrange
    payload = {"content": "a" * 281}

    # Act
    response = client.post("/api/v1/posts", json=payload, headers=auth_header)

    # Assert
    assert response.status_code == 422


def test_create_post_no_auth(client: TestClient):
    # Act
    response = client.post("/api/v1/posts", json={"content": "test"})

    # Assert
    assert response.status_code == 403


def test_get_post(client: TestClient, auth_header: dict):
    # Arrange
    create_response = client.post("/api/v1/posts", json={"content": "取得テスト"}, headers=auth_header)
    post_id = create_response.json()["data"]["id"]

    # Act
    response = client.get(f"/api/v1/posts/{post_id}", headers=auth_header)

    # Assert
    assert response.status_code == 200
    assert response.json()["data"]["content"] == "取得テスト"


def test_get_post_not_found(client: TestClient, auth_header: dict):
    # Act
    response = client.get("/api/v1/posts/99999", headers=auth_header)

    # Assert
    assert response.status_code == 404


def test_update_post(client: TestClient, auth_header: dict):
    # Arrange
    create_response = client.post("/api/v1/posts", json={"content": "編集前"}, headers=auth_header)
    post_id = create_response.json()["data"]["id"]

    # Act
    response = client.put(f"/api/v1/posts/{post_id}", json={"content": "編集後"}, headers=auth_header)

    # Assert
    assert response.status_code == 200
    assert response.json()["data"]["content"] == "編集後"


def test_update_post_forbidden(client: TestClient, auth_header: dict, second_auth_header: dict):
    # Arrange
    create_response = client.post("/api/v1/posts", json={"content": "他人の投稿"}, headers=auth_header)
    post_id = create_response.json()["data"]["id"]

    # Act
    response = client.put(f"/api/v1/posts/{post_id}", json={"content": "編集"}, headers=second_auth_header)

    # Assert
    assert response.status_code == 403


def test_delete_post(client: TestClient, auth_header: dict):
    # Arrange
    create_response = client.post("/api/v1/posts", json={"content": "削除テスト"}, headers=auth_header)
    post_id = create_response.json()["data"]["id"]

    # Act
    response = client.delete(f"/api/v1/posts/{post_id}", headers=auth_header)

    # Assert
    assert response.status_code == 200
    assert response.json()["data"]["message"] == "投稿を削除しました"


def test_delete_post_forbidden(client: TestClient, auth_header: dict, second_auth_header: dict):
    # Arrange
    create_response = client.post("/api/v1/posts", json={"content": "他人の投稿"}, headers=auth_header)
    post_id = create_response.json()["data"]["id"]

    # Act
    response = client.delete(f"/api/v1/posts/{post_id}", headers=second_auth_header)

    # Assert
    assert response.status_code == 403
