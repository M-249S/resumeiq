import logging
import os
import time

from app.services.mock_service import (
    analyze_resume as mock_analyze,
    rewrite_resume as mock_rewrite,
)

from app.services.gemini_service import (
    analyze_resume as gemini_analyze,
    rewrite_resume as gemini_rewrite,
)

from app.services.openrouter_service import (
    analyze_resume as openrouter_analyze,
)

logger = logging.getLogger(__name__)

GEMINI_RETRIES = 3
RETRY_DELAY = 2


# ---------------------------------------------------
# Helpers
# ---------------------------------------------------

def _retry(func, *args, retries=3, delay=2, provider="AI", **kwargs):
    """
    Generic retry helper.
    """

    for attempt in range(1, retries + 1):

        try:

            return func(*args, **kwargs)

        except Exception as exc:
            logger.warning(
                "%s call failed on attempt %d/%d: %s",
                provider,
                attempt,
                retries,
                exc,
            )
            if attempt < retries:
                time.sleep(delay)

    return None


# ---------------------------------------------------
# Resume Analysis
# ---------------------------------------------------

def analyze_resume(
    resume_text: str,
    job_description: str = "",
    allow_mock: bool = True,
):
    """
    Provider Priority

    1. Gemini
    2. OpenRouter
    3. Mock (only when allow_mock is True)

    With allow_mock=False the function returns None instead of fabricated
    results when every real provider fails, so callers that must not show
    fake data (e.g. the public demo) can report an outage instead.
    """

    # -------------------------
    # Gemini
    # -------------------------

    if os.getenv("GEMINI_API_KEY"):

        result = _retry(
            gemini_analyze,
            resume_text=resume_text,
            job_description=job_description,
            retries=GEMINI_RETRIES,
            delay=RETRY_DELAY,
            provider="Gemini",
        )

        if result is not None:
            return result

    # -------------------------
    # OpenRouter
    # -------------------------

    if os.getenv("OPENROUTER_API_KEY"):

        try:

            return openrouter_analyze(
                resume_text=resume_text,
                job_description=job_description,
            )

        except Exception as exc:
            logger.warning(
                "OpenRouter analysis failed, falling back to mock: %s", exc
            )

    # -------------------------
    # Mock
    # -------------------------

    if not allow_mock:
        return None

    return mock_analyze(
        resume_text=resume_text,
        job_description=job_description,
    )


# ---------------------------------------------------
# Resume Rewrite
# ---------------------------------------------------

def rewrite_resume(
    resume_text: str,
):
    """
    Rewrite Priority

    1. Gemini
    2. Mock
    """

    if os.getenv("GEMINI_API_KEY"):

        result = _retry(
            gemini_rewrite,
            resume_text=resume_text,
            retries=GEMINI_RETRIES,
            delay=RETRY_DELAY,
            provider="Gemini Rewrite",
        )

        if result is not None:
            return result

    return mock_rewrite(
        resume_text=resume_text,
    )
