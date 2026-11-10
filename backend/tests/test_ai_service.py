"""
analyze_resume must tell the real AI providers when no job description was
given (otherwise they score everything 0), while the mock keeps the raw value.
No network: providers are replaced by recorders.
"""
from app.services import ai_service


def _recorder(calls, result=None):
    def _fake(**kwargs):
        calls.append(kwargs)
        return result if result is not None else {"score": 1}

    return _fake


def test_openrouter_gets_note_when_job_description_empty(monkeypatch):
    calls = []
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setenv("OPENROUTER_API_KEY", "k")
    monkeypatch.setattr(ai_service, "openrouter_analyze", _recorder(calls))

    ai_service.analyze_resume("resume text", "   ")

    assert calls[0]["job_description"] == ai_service.NO_JOB_DESCRIPTION_NOTE


def test_openrouter_keeps_real_job_description(monkeypatch):
    calls = []
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setenv("OPENROUTER_API_KEY", "k")
    monkeypatch.setattr(ai_service, "openrouter_analyze", _recorder(calls))

    ai_service.analyze_resume("resume text", "Python developer")

    assert calls[0]["job_description"] == "Python developer"


def test_gemini_gets_note_when_job_description_empty(monkeypatch):
    calls = []
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    monkeypatch.setattr(ai_service, "gemini_analyze", _recorder(calls))

    ai_service.analyze_resume("resume text", "")

    assert calls[0]["job_description"] == ai_service.NO_JOB_DESCRIPTION_NOTE


def test_mock_keeps_empty_job_description(monkeypatch):
    calls = []
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.setattr(ai_service, "mock_analyze", _recorder(calls))

    ai_service.analyze_resume("resume text", "")

    assert calls[0]["job_description"] == ""
