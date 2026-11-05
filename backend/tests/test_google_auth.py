"""
Tests for POST /auth/google.

verify_google_credential is monkeypatched, so no network call to Google is
made. The database is an in-memory SQLite, like test_resume_history.py.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth import service
from app.db.session import get_db
from app.main import app
from app.models.base import Base
from app.models.user import User

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

CLAIMS = {
    "sub": "google-123",
    "email": "Ada@Example.com",
    "email_verified": True,
    "name": "Ada Lovelace",
}


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def _fresh_schema():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def _claims(monkeypatch, claims):
    monkeypatch.setattr(service, "verify_google_credential", lambda _c: claims)


def _users():
    db = TestingSessionLocal()
    try:
        return db.query(User).all()
    finally:
        db.close()


def test_new_google_user_is_created_and_gets_tokens(client, monkeypatch):
    _claims(monkeypatch, CLAIMS)

    response = client.post("/auth/google", json={"credential": "tok"})

    assert response.status_code == 200
    body = response.json()
    assert body["access_token"] and body["refresh_token"]
    users = _users()
    assert len(users) == 1
    assert users[0].email == "ada@example.com"
    assert users[0].google_sub == "google-123"
    assert users[0].full_name == "Ada Lovelace"


def test_second_google_login_reuses_the_same_user(client, monkeypatch):
    _claims(monkeypatch, CLAIMS)
    client.post("/auth/google", json={"credential": "tok"})
    client.post("/auth/google", json={"credential": "tok"})
    assert len(_users()) == 1


def test_existing_password_account_is_linked(client, monkeypatch):
    db = TestingSessionLocal()
    db.add(User(full_name="Ada", email="ada@example.com", hashed_password="x"))
    db.commit()
    db.close()
    _claims(monkeypatch, CLAIMS)

    response = client.post("/auth/google", json={"credential": "tok"})

    assert response.status_code == 200
    users = _users()
    assert len(users) == 1
    assert users[0].google_sub == "google-123"


def test_unverified_google_email_is_rejected(client, monkeypatch):
    _claims(monkeypatch, {**CLAIMS, "email_verified": False})

    response = client.post("/auth/google", json={"credential": "tok"})

    assert response.status_code == 401
    assert _users() == []


def test_invalid_credential_returns_401(client, monkeypatch):
    def boom(_c):
        raise ValueError("Invalid Google credential.")

    monkeypatch.setattr(service, "verify_google_credential", boom)

    response = client.post("/auth/google", json={"credential": "bad"})

    assert response.status_code == 401


def test_missing_client_id_returns_503(client, monkeypatch):
    monkeypatch.delenv("GOOGLE_CLIENT_ID", raising=False)

    response = client.post("/auth/google", json={"credential": "tok"})

    assert response.status_code == 503


def test_disabled_account_is_rejected(client, monkeypatch):
    db = TestingSessionLocal()
    db.add(
        User(
            full_name="Ada",
            email="ada@example.com",
            hashed_password="x",
            google_sub="google-123",
            is_active=False,
        )
    )
    db.commit()
    db.close()
    _claims(monkeypatch, CLAIMS)

    response = client.post("/auth/google", json={"credential": "tok"})

    assert response.status_code == 401
