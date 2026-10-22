"""
Tests for the resume history endpoints (/resume/history, /resume/history/{id}).

These use a real in-memory SQLite database (overriding get_db) instead of
the fake Postgres DSN from conftest.py, since the endpoints under test
actually run queries. get_current_user is overridden directly to a fixed
user rather than going through the JWT login flow, which is already
covered by test_security.py.
"""
from datetime import datetime, timedelta

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

FAKE_USER = User(id=1, full_name="Test User", email="test@example.com", hashed_password="x")

SAMPLE_ANALYSIS = {
    "score": 0,
    "match_score": 0,
    "ats_level": "Good",
    "summary": "Looks solid.",
    "formatting_score": 1,
    "keyword_score": 1,
    "experience_score": 1,
    "skills_score": 1,
    "education_score": 1,
    "readability_score": 1,
    "strengths": [],
    "weaknesses": [],
    "matching_skills": [],
    "missing_skills": [],
    "suggestions": [],
}


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_current_user():
    return FAKE_USER


def _seed_analysis(user_id: int, filename: str, score: int, created_at=None) -> ResumeAnalysis:
    db = TestingSessionLocal()
    analysis_payload = {**SAMPLE_ANALYSIS, "score": score, "match_score": score}
    record = ResumeAnalysis(
        user_id=user_id,
        filename=filename,
        score=score,
        match_score=score,
        analysis=analysis_payload,
        created_at=created_at or datetime.utcnow(),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    db.close()
    return record


@pytest.fixture(autouse=True)
def _fresh_schema():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_history_list_is_empty_for_new_user(client):
    response = client.get("/resume/history")

    assert response.status_code == 200
    assert response.json() == []


def test_history_list_returns_own_records_newest_first(client):
    _seed_analysis(1, "old.pdf", 60, created_at=datetime.utcnow() - timedelta(days=1))
    _seed_analysis(1, "new.pdf", 80)

    response = client.get("/resume/history")

    assert response.status_code == 200
    body = response.json()
    assert [item["filename"] for item in body] == ["new.pdf", "old.pdf"]
    # The list endpoint is a summary — no full analysis payload per row.
    assert "analysis" not in body[0]


def test_history_list_excludes_other_users_records(client):
    _seed_analysis(2, "not-mine.pdf", 70)

    response = client.get("/resume/history")

    assert response.status_code == 200
    assert response.json() == []


def test_history_detail_returns_full_analysis(client):
    record = _seed_analysis(1, "resume.pdf", 90)

    response = client.get(f"/resume/history/{record.id}")

    assert response.status_code == 200
    body = response.json()
    assert body["filename"] == "resume.pdf"
    assert body["analysis"]["score"] == 90


def test_history_detail_404_for_missing_record(client):
    response = client.get("/resume/history/999")

    assert response.status_code == 404


def test_history_detail_404_for_other_users_record(client):
    record = _seed_analysis(2, "not-mine.pdf", 70)

    response = client.get(f"/resume/history/{record.id}")

    assert response.status_code == 404


def test_delete_history_removes_record(client):
    record = _seed_analysis(1, "resume.pdf", 90)

    delete_response = client.delete(f"/resume/history/{record.id}")
    assert delete_response.status_code == 204

    list_response = client.get("/resume/history")
    assert list_response.json() == []


def test_delete_history_404_for_other_users_record(client):
    record = _seed_analysis(2, "not-mine.pdf", 70)

    response = client.delete(f"/resume/history/{record.id}")

    assert response.status_code == 404
