"""
Tests for DELETE /users/me (self-serve account deletion).

Real in-memory SQLite (overriding get_db), like test_resume_history.py.
get_current_user is overridden to a user whose id/email match a seeded row.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth.dependencies import get_current_user
from app.db.session import get_db
from app.main import app
from app.models.base import Base
from app.models.user import User
from app.resume.models import ResumeAnalysis

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

PAYLOAD = {
    "score": 1, "match_score": 1, "ats_level": "Good", "summary": "ok",
    "formatting_score": 1, "keyword_score": 1, "experience_score": 1,
    "skills_score": 1, "education_score": 1, "readability_score": 1,
    "strengths": [], "weaknesses": [], "matching_skills": [],
    "missing_skills": [], "suggestions": [],
}


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def _seed():
    """Two users, each with one analysis. Returns (me_id, other_id)."""
    db = TestingSessionLocal()
    me = User(full_name="Me", email="Me@Example.com", hashed_password="x")
    other = User(full_name="Other", email="other@example.com", hashed_password="x")
    db.add_all([me, other])
    db.commit()
    for user in (me, other):
        db.add(
            ResumeAnalysis(
                user_id=user.id, filename="cv.pdf", score=1, match_score=1,
                analysis=PAYLOAD,
            )
        )
    db.commit()
    ids = (me.id, other.id)
    db.close()
    return ids


@pytest.fixture(autouse=True)
def _fresh_schema():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def me_id():
    me, _other = _seed()
    return me


@pytest.fixture
def client(me_id):
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = lambda: User(
        id=me_id, full_name="Me", email="Me@Example.com", hashed_password="x"
    )
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def _counts():
    db = TestingSessionLocal()
    result = (
        db.query(User).count(),
        db.query(ResumeAnalysis).count(),
    )
    db.close()
    return result


def test_wrong_confirmation_is_rejected_and_nothing_is_deleted(client):
    response = client.request(
        "DELETE", "/users/me", json={"confirm_email": "someone@else.com"}
    )

    assert response.status_code == 400
    assert _counts() == (2, 2)


def test_confirmation_is_required(client):
    response = client.request("DELETE", "/users/me", json={})

    assert response.status_code == 422
    assert _counts() == (2, 2)


def test_deletes_user_and_their_analyses_only(client, me_id):
    # Case and surrounding spaces in the typed email do not matter.
    response = client.request(
        "DELETE", "/users/me", json={"confirm_email": "  me@example.COM "}
    )

    assert response.status_code == 204
    # One user and one analysis remain: the other user's.
    assert _counts() == (1, 1)
    db = TestingSessionLocal()
    assert db.get(User, me_id) is None
    assert db.query(User).one().email == "other@example.com"
    db.close()


def test_requires_authentication():
    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as anonymous:
            response = anonymous.request(
                "DELETE", "/users/me", json={"confirm_email": "me@example.com"}
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 401
