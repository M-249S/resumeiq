import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "google/gemma-4-26b-a4b-it:free",
).strip()

_client = None


def _get_client() -> OpenAI:
    global _client

    if _client is None:
        api_key = os.getenv("OPENROUTER_API_KEY")

        if not api_key:
            raise RuntimeError("OPENROUTER_API_KEY is not set.")

        _client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key.strip(),
        )

    return _client


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

    response = _get_client().chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        temperature=0.3,
        timeout=120,
    )

    text = response.choices[0].message.content.strip()

    if text.startswith("```json"):
        text = text[7:]

    elif text.startswith("```"):
        text = text[3:]

    if text.endswith("```"):
        text = text[:-3]

    text = text.strip()

    return json.loads(text)
