"""
Tests for the per-user daily AI allowance (app/services/user_quota.py and
the ai_quota dependency on the AI endpoints in app/routers/resume.py).

The AI call and PDF parsing are replaced with stubs: these tests are about
how requests are counted, not about analysis quality.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth.dependencies import get_current_user
from app.core.limiter import limiter
from app.db.session import get_db
from app.main import app
from app.models.base import Base
from app.models.user import User
from app.routers import resume as resume_router
from app.services.user_quota import UserDailyQuota

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

ANALYSIS = {
    "score": 70,
    "match_score": 0,
    "ats_level": "N/A",
    "summary": "ok",
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


# --- the counter on its own -------------------------------------------------


def test_quota_allows_up_to_the_limit_then_refuses():
    quota = UserDailyQuota(2)

    assert quota.try_consume(1) is True
    assert quota.try_consume(1) is True
    assert quota.try_consume(1) is False


def test_quota_is_tracked_per_user():
    quota = UserDailyQuota(1)

    assert quota.try_consume(1) is True
    assert quota.try_consume(1) is False
    assert quota.try_consume(2) is True


def test_refund_gives_one_unit_back_and_never_goes_negative():
    quota = UserDailyQuota(1)

    quota.refund(1)  # nothing used yet: must not create credit
    assert quota.try_consume(1) is True
    assert quota.try_consume(1) is False

    quota.refund(1)
    assert quota.try_consume(1) is True
    assert quota.try_consume(1) is False


def test_quota_resets_on_a_new_utc_day(monkeypatch):
    quota = UserDailyQuota(1)
    assert quota.try_consume(1) is True
    assert quota.try_consume(1) is False

    monkeypatch.setattr(UserDailyQuota, "_today", staticmethod(lambda: "2099-01-01"))

    assert quota.try_consume(1) is True


# --- through the endpoint ---------------------------------------------------


@pytest.fixture
def api(monkeypatch):
    Base.metadata.create_all(bind=engine)
    limiter.reset()

    current = {"user": User(id=1, full_name="A", email="a@example.com", hashed_password="x")}

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    monkeypatch.setattr(resume_router, "user_quota", UserDailyQuota(2))
    monkeypatch.setattr(resume_router, "extract_text_from_pdf", lambda _b: ("resume text", 1))
    monkeypatch.setattr(resume_router, "analyze_resume", lambda **_kw: dict(ANALYSIS))

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = lambda: current["user"]
    with TestClient(app) as client:
        yield client, current, monkeypatch
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


def _upload(client):
    return client.post(
        "/resume/upload",
        files={"file": ("cv.pdf", b"%PDF-1.4 stub", "application/pdf")},
    )


def test_upload_is_refused_once_the_daily_allowance_is_used(api):
    client, _, _ = api

    assert _upload(client).status_code == 200
    assert _upload(client).status_code == 200

    blocked = _upload(client)
    assert blocked.status_code == 429
    assert "today's limit of 2" in blocked.json()["detail"]


def test_each_user_has_their_own_allowance(api):
    client, current, _ = api

    _upload(client)
    _upload(client)
    assert _upload(client).status_code == 429

    current["user"] = User(id=2, full_name="B", email="b@example.com", hashed_password="x")
    assert _upload(client).status_code == 200


def test_failed_ai_call_does_not_use_up_the_allowance(api):
    client, _, monkeypatch = api
    monkeypatch.setattr(resume_router, "analyze_resume", lambda **_kw: None)

    # Each failure is refunded, so more attempts than the limit still reach the handler.
    for _ in range(3):
        assert _upload(client).status_code == 500


def test_rejected_upload_does_not_use_up_the_allowance(api):
    client, _, _ = api

    for _ in range(3):
        bad = client.post(
            "/resume/upload",
            files={"file": ("cv.txt", b"not a pdf", "text/plain")},
        )
        assert bad.status_code == 400

    assert _upload(client).status_code == 200
