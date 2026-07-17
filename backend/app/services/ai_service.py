import os

from app.services.mock_service import (
    analyze_resume as mock_analyze,
    rewrite_resume as mock_rewrite,
)

from app.services.gemini_service import (
    analyze_resume as gemini_analyze,
    rewrite_resume as gemini_rewrite,
)

from app.services.openai_service import (
    analyze_resume as openai_analyze,
)


def analyze_resume(
    resume_text: str,
    job_description: str = "",
):
    """
    Select the available AI provider automatically.
    """

    # Use Gemini if API key exists
    if os.getenv("GEMINI_API_KEY"):
        try:
            return gemini_analyze(
                resume_text=resume_text,
                job_description=job_description,
            )
        except Exception as e:
            print(f"[Gemini] Failed: {e}")

    # Use OpenAI if API key exists
    if os.getenv("OPENAI_API_KEY"):
        try:
            return openai_analyze(
                resume_text=resume_text,
                job_description=job_description,
            )
        except Exception as e:
            print(f"[OpenAI] Failed: {e}")

    # Fallback to Mock service
    print("[Mock] Using local analyzer.")

    return mock_analyze(
        resume_text=resume_text,
        job_description=job_description,
    )


def rewrite_resume(
    resume_text: str,
):
    """
    Rewrite resume using the available AI provider.
    """

    # Use Gemini if API key exists
    if os.getenv("GEMINI_API_KEY"):
        try:
            return gemini_rewrite(
                resume_text=resume_text,
            )
        except Exception as e:
            print(f"[Gemini Rewrite] Failed: {e}")

    # Fallback to Mock service
    print("[Mock] Using local resume rewrite.")

    return mock_rewrite(
        resume_text=resume_text,
    )