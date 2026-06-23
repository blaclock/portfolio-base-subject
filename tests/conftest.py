import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.models.base import Base
from app.database.session import get_db


TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    """テストごとにテーブルを再作成する"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """TestClient を返すフィクスチャ"""
    return TestClient(app)


@pytest.fixture
def registered_user(client: TestClient) -> dict:
    """ユーザ登録済みの状態を返すフィクスチャ"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
            "display_name": "テストユーザ",
        },
    )
    data = response.json()["data"]
    return {"token": data["token"], "user": data["user"]}


@pytest.fixture
def auth_header(registered_user: dict) -> dict:
    """認証ヘッダーを返すフィクスチャ"""
    return {"Authorization": f"Bearer {registered_user['token']}"}


@pytest.fixture
def second_user(client: TestClient) -> dict:
    """2人目のユーザを返すフィクスチャ"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "user2",
            "email": "user2@example.com",
            "password": "password123",
            "display_name": "ユーザ2",
        },
    )
    data = response.json()["data"]
    return {"token": data["token"], "user": data["user"]}


@pytest.fixture
def second_auth_header(second_user: dict) -> dict:
    """2人目の認証ヘッダーを返すフィクスチャ"""
    return {"Authorization": f"Bearer {second_user['token']}"}
