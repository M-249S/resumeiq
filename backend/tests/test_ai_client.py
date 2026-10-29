"""
Tests for the OpenRouter client wrapper: retry on transient errors,
fallback models, and the clean 503 the cover-letter endpoint returns when
the AI is unavailable. No network calls — the OpenAI client is faked.
"""
import json
from types import SimpleNamespace

import httpx
import pytest
from fastapi.testclient import TestClient
from openai import AuthenticationError, RateLimitError

from app.auth.dependencies import get_current_user
from app.main import app
from app.models.user import User
from app.services import ai_client, openrouter_service


def _rate_limit_error():
    request = httpx.Request("POST", "https://openrouter.ai/api/v1/chat/completions")
    response = httpx.Response(429, request=request)
    return RateLimitError("rate limited", response=response, body=None)


def _auth_error():
    request = httpx.Request("POST", "https://openrouter.ai/api/v1/chat/completions")
    response = httpx.Response(401, request=request)
    return AuthenticationError("bad key", response=response, body=None)


def _reply(text):
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=text))]
    )


class FakeClient:
    """Plays back one scripted outcome per call: an Exception or reply text."""

    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.models_called = []
        self.chat = SimpleNamespace(
            completions=SimpleNamespace(create=self._create)
        )

    def _create(self, **kwargs):
        self.models_called.append(kwargs["model"])
        outcome = self.outcomes.pop(0)

        if isinstance(outcome, Exception):
            raise outcome

        return _reply(outcome)


@pytest.fixture(autouse=True)
def fast_env(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setenv("OPENROUTER_MODEL", "model-a")
    monkeypatch.setenv("OPENROUTER_FALLBACK_MODELS", "model-b, model-c")
    monkeypatch.setenv("OPENROUTER_RETRIES", "2")
    monkeypatch.setenv("OPENROUTER_RETRY_DELAY", "0")


def _use(monkeypatch, outcomes):
    client = FakeClient(outcomes)
    monkeypatch.setattr(ai_client, "_get_client", lambda: client)
    return client


def test_get_models_order_and_dedup(monkeypatch):
    monkeypatch.setenv("OPENROUTER_FALLBACK_MODELS", "model-b, model-a, ,model-c")

    assert ai_client.get_models() == ["model-a", "model-b", "model-c"]


def test_get_models_default_when_unset(monkeypatch):
    monkeypatch.delenv("OPENROUTER_MODEL")
    monkeypatch.delenv("OPENROUTER_FALLBACK_MODELS")

    assert ai_client.get_models() == [ai_client.DEFAULT_MODEL]


def test_returns_first_successful_reply(monkeypatch):
    client = _use(monkeypatch, ["hello"])

    assert ai_client.generate("hi") == "hello"
    assert client.models_called == ["model-a"]


def test_retries_same_model_on_429(monkeypatch):
    client = _use(monkeypatch, [_rate_limit_error(), "recovered"])

    assert ai_client.generate("hi") == "recovered"
    assert client.models_called == ["model-a", "model-a"]


def test_falls_back_to_next_model_after_retries(monkeypatch):
    client = _use(
        monkeypatch,
        [_rate_limit_error(), _rate_limit_error(), "from-b"],
    )

    assert ai_client.generate("hi") == "from-b"
    assert client.models_called == ["model-a", "model-a", "model-b"]


def test_non_transient_error_skips_to_next_model(monkeypatch):
    client = _use(monkeypatch, [ValueError("model removed"), "from-b"])

    assert ai_client.generate("hi") == "from-b"
    assert client.models_called == ["model-a", "model-b"]


def test_empty_reply_is_retried(monkeypatch):
    client = _use(monkeypatch, ["   ", "real answer"])

    assert ai_client.generate("hi") == "real answer"
    assert client.models_called == ["model-a", "model-a"]


def test_raises_ai_unavailable_when_everything_fails(monkeypatch):
    client = _use(monkeypatch, [_rate_limit_error()] * 6)

    with pytest.raises(ai_client.AIUnavailableError):
        ai_client.generate("hi")

    assert client.models_called == [
        "model-a", "model-a", "model-b", "model-b", "model-c", "model-c",
    ]


def test_bad_api_key_fails_fast(monkeypatch):
    client = _use(monkeypatch, [_auth_error(), "never reached"])

    with pytest.raises(ai_client.AIUnavailableError):
        ai_client.generate("hi")

    assert client.models_called == ["model-a"]


def test_missing_api_key_raises_ai_unavailable(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY")
    monkeypatch.setattr(ai_client, "_client", None)

    with pytest.raises(ai_client.AIUnavailableError):
        ai_client.generate("hi")


def test_analysis_retries_on_invalid_json(monkeypatch):
    good = {"score": 50}
    replies = iter(["not json at all", "```json\n" + json.dumps(good) + "\n```"])
    monkeypatch.setattr(
        openrouter_service, "generate", lambda *a, **k: next(replies)
    )

    assert openrouter_service.analyze_resume("resume", "job") == good


def test_analysis_raises_after_repeated_invalid_json(monkeypatch):
    monkeypatch.setattr(
        openrouter_service, "generate", lambda *a, **k: "still not json"
    )

    with pytest.raises(json.JSONDecodeError):
        openrouter_service.analyze_resume("resume", "job")


def test_cover_letter_endpoint_returns_503_when_ai_unavailable(monkeypatch):
    from app.routers import resume as resume_router

    def boom(**kwargs):
        raise ai_client.AIUnavailableError("busy")

    monkeypatch.setattr(resume_router, "generate_cover_letter", boom)
    monkeypatch.setattr(
        resume_router, "extract_text_from_pdf", lambda data: ("resume text", 1)
    )

    fake_user = User(id=1, full_name="T", email="t@example.com", hashed_password="x")
    previous = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_current_user] = lambda: fake_user

    try:
        response = TestClient(app).post(
            "/resume/cover-letter",
            files={"file": ("cv.pdf", b"%PDF-1.4", "application/pdf")},
            data={"job_description": "job"},
        )
    finally:
        if previous is None:
            app.dependency_overrides.pop(get_current_user, None)
        else:
            app.dependency_overrides[get_current_user] = previous

    assert response.status_code == 503
    assert "busy" in response.json()["detail"].lower()
