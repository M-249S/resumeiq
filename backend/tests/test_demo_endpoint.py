"""
Tests for POST /resume/demo (the unauthenticated demo analysis).

PDF parsing and the AI call are monkeypatched, so no real PDF or provider
is needed. No database is involved: the endpoint must not store anything.
"""
import pytest
from fastapi.testclient import TestClient

from app.core.limiter import client_key, limiter
from app.main import app
from app.routers import resume as resume_router
from app.services.demo_budget import DailyBudget

ANALYSIS = {
    "score": 62,
    "match_score": 48,
    "ats_level": "Good",
    "summary": "Solid structure.",
    "formatting_score": 80,
    "keyword_score": 45,
    "experience_score": 60,
    "skills_score": 55,
    "education_score": 70,
    "readability_score": 85,
    "strengths": ["Clear structure"],
    "weaknesses": ["Few metrics"],
    "matching_skills": ["Python"],
    "missing_skills": ["Docker"],
    "suggestions": ["Add measurable results"],
}


@pytest.fixture(autouse=True)
def _isolated(monkeypatch):
    limiter.reset()
    monkeypatch.setattr(resume_router, "demo_budget", DailyBudget(100))
    monkeypatch.setattr(
        resume_router, "extract_text_from_pdf", lambda _b: ("resume text", 1)
    )
    monkeypatch.setattr(
        resume_router, "analyze_resume", lambda **_kw: dict(ANALYSIS)
    )
    yield
    limiter.reset()


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def _post(client, content=b"%PDF-1.4 x", content_type="application/pdf", **data):
    return client.post(
        "/resume/demo",
        files={"file": ("cv.pdf", content, content_type)},
        data=data,
    )


def test_guest_can_analyze_without_auth(client):
    response = _post(client, job_description="Python developer")

    assert response.status_code == 200
    body = response.json()
    assert body["analysis"]["score"] == 62
    assert body["filename"] == "cv.pdf"


def test_rejects_non_pdf(client):
    assert _post(client, content_type="text/plain").status_code == 400


def test_rejects_oversized_file(client):
    big = b"0" * (resume_router.DEMO_MAX_BYTES + 1)
    assert _post(client, content=big).status_code == 413


def test_rejects_too_many_pages(client, monkeypatch):
    monkeypatch.setattr(
        resume_router,
        "extract_text_from_pdf",
        lambda _b: ("text", resume_router.DEMO_MAX_PAGES + 1),
    )
    assert _post(client).status_code == 400


def test_rejects_pdf_without_text(client, monkeypatch):
    monkeypatch.setattr(
        resume_router, "extract_text_from_pdf", lambda _b: ("   \n", 1)
    )
    assert _post(client).status_code == 400


def test_unreadable_pdf_returns_400(client, monkeypatch):
    def boom(_b):
        raise ValueError("broken")

    monkeypatch.setattr(resume_router, "extract_text_from_pdf", boom)
    assert _post(client).status_code == 400


def test_ai_outage_returns_503_and_refunds_budget(client, monkeypatch):
    budget = DailyBudget(1)
    monkeypatch.setattr(resume_router, "demo_budget", budget)
    monkeypatch.setattr(resume_router, "analyze_resume", lambda **_kw: None)

    assert _post(client).status_code == 503
    assert budget.try_consume() is True  # the failed attempt was refunded


def test_mock_fallback_is_never_used(client, monkeypatch):
    seen = {}

    def fake(**kwargs):
        seen.update(kwargs)
        return dict(ANALYSIS)

    monkeypatch.setattr(resume_router, "analyze_resume", fake)
    _post(client)

    assert seen["allow_mock"] is False


def test_inputs_are_truncated(client, monkeypatch):
    seen = {}
    monkeypatch.setattr(
        resume_router,
        "extract_text_from_pdf",
        lambda _b: ("x" * (resume_router.DEMO_MAX_RESUME_CHARS + 500), 1),
    )

    def fake(**kwargs):
        seen.update(kwargs)
        return dict(ANALYSIS)

    monkeypatch.setattr(resume_router, "analyze_resume", fake)
    _post(client, job_description="j" * (resume_router.DEMO_MAX_JOB_CHARS + 500))

    assert len(seen["resume_text"]) == resume_router.DEMO_MAX_RESUME_CHARS
    assert len(seen["job_description"]) == resume_router.DEMO_MAX_JOB_CHARS


def test_per_ip_rate_limit_returns_429(client):
    for _ in range(3):
        assert _post(client).status_code == 200
    assert _post(client).status_code == 429


def test_daily_budget_exhausted_returns_429(client, monkeypatch):
    monkeypatch.setattr(resume_router, "demo_budget", DailyBudget(0))
    response = _post(client)

    assert response.status_code == 429
    assert "limit for today" in response.json()["detail"]


def test_client_key_ignores_forwarded_header_by_default(monkeypatch):
    monkeypatch.delenv("TRUST_PROXY_HEADERS", raising=False)

    class Req:
        headers = {"x-forwarded-for": "9.9.9.9"}
        client = type("C", (), {"host": "10.0.0.1"})()

    assert client_key(Req()) == "10.0.0.1"


def test_client_key_uses_forwarded_header_when_trusted(monkeypatch):
    monkeypatch.setenv("TRUST_PROXY_HEADERS", "1")

    class Req:
        headers = {"x-forwarded-for": "9.9.9.9, 10.0.0.1"}
        client = type("C", (), {"host": "10.0.0.1"})()

    assert client_key(Req()) == "9.9.9.9"
