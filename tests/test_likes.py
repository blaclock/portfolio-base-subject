from fastapi.testclient import TestClient


def test_like_post(client: TestClient, auth_header: dict, second_user: dict, second_auth_header: dict):
    # Arrange
    create_response = client.post("/api/v1/posts", json={"content": "いいねテスト"}, headers=auth_header)
    post_id = create_response.json()["data"]["id"]

    # Act
    response = client.post(f"/api/v1/posts/{post_id}/like", headers=second_auth_header)

    # Assert
    assert response.status_code == 201
    assert response.json()["data"]["like_count"] == 1


def test_like_own_post(client: TestClient, auth_header: dict):
    # Arrange
    create_response = client.post("/api/v1/posts", json={"content": "自分の投稿"}, headers=auth_header)
    post_id = create_response.json()["data"]["id"]

    # Act
    response = client.post(f"/api/v1/posts/{post_id}/like", headers=auth_header)

    # Assert
    assert response.status_code == 400


def test_like_already_liked(client: TestClient, auth_header: dict, second_user: dict, second_auth_header: dict):
    # Arrange
    create_response = client.post("/api/v1/posts", json={"content": "重複いいね"}, headers=auth_header)
    post_id = create_response.json()["data"]["id"]
    client.post(f"/api/v1/posts/{post_id}/like", headers=second_auth_header)

    # Act
    response = client.post(f"/api/v1/posts/{post_id}/like", headers=second_auth_header)

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "ALREADY_LIKED"


def test_like_nonexistent_post(client: TestClient, auth_header: dict):
    # Act
    response = client.post("/api/v1/posts/99999/like", headers=auth_header)

    # Assert
    assert response.status_code == 404


def test_unlike_post(client: TestClient, auth_header: dict, second_user: dict, second_auth_header: dict):
    # Arrange
    create_response = client.post("/api/v1/posts", json={"content": "いいね解除"}, headers=auth_header)
    post_id = create_response.json()["data"]["id"]
    client.post(f"/api/v1/posts/{post_id}/like", headers=second_auth_header)

    # Act
    response = client.delete(f"/api/v1/posts/{post_id}/like", headers=second_auth_header)

    # Assert
    assert response.status_code == 200
    assert response.json()["data"]["like_count"] == 0


def test_unlike_not_liked(client: TestClient, auth_header: dict, second_user: dict, second_auth_header: dict):
    # Arrange
    create_response = client.post("/api/v1/posts", json={"content": "未いいね"}, headers=auth_header)
    post_id = create_response.json()["data"]["id"]

    # Act
    response = client.delete(f"/api/v1/posts/{post_id}/like", headers=second_auth_header)

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "NOT_LIKED"
