import json
import logging

from dotenv import load_dotenv

from app.services.ai_client import generate

load_dotenv()

logger = logging.getLogger(__name__)

# The model sometimes returns malformed JSON on long inputs; one more
# attempt usually fixes it.
JSON_ATTEMPTS = 2


def analyze_resume(
    resume_text: str,
    job_description: str = "",
):
    prompt = f"""
You are an ATS Resume Expert.

Analyze the following resume.

Return ONLY valid JSON.

Resume:

{resume_text}

Job Description:

{job_description}

Return this exact schema:

{{
  "score": 0,
  "match_score": 0,
  "ats_level": "",
  "summary": "",

  "formatting_score": 0,
  "keyword_score": 0,
  "experience_score": 0,
  "skills_score": 0,
  "education_score": 0,
  "readability_score": 0,

  "strengths": [],
  "weaknesses": [],
  "matching_skills": [],
  "missing_skills": [],
  "suggestions": []
}}
"""

    last_error = None

    for attempt in range(1, JSON_ATTEMPTS + 1):
        text = generate(prompt, temperature=0.3, timeout=120).strip()

        if text.startswith("```json"):
            text = text[7:]

        elif text.startswith("```"):
            text = text[3:]

        if text.endswith("```"):
            text = text[:-3]

        try:
            return json.loads(text.strip())

        except json.JSONDecodeError as exc:
            last_error = exc
            logger.warning(
                "OpenRouter returned invalid JSON (attempt %d/%d): %s",
                attempt,
                JSON_ATTEMPTS,
                exc,
            )

    raise last_error
