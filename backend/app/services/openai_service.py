import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def analyze_resume(
    resume_text: str,
    job_description: str = "",
):
    model = os.getenv(
        "OPENAI_MODEL",
        "gpt-5-mini",
    )

    prompt = f"""
You are an expert ATS Resume Reviewer.

Analyze the resume against the job description.

Return ONLY valid JSON.

Resume:

{resume_text}

Job Description:

{job_description}

Return:

{{
  "score": 0,
  "match_score": 0,
  "strengths": [],
  "weaknesses": [],
  "matching_skills": [],
  "missing_skills": [],
  "suggestions": []
}}
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        response_format={"type": "json_object"},
    )

    text = response.choices[0].message.content

    return json.loads(text)


def rewrite_resume(
    resume_text: str,
):
    model = os.getenv(
        "OPENAI_MODEL",
        "gpt-5-mini",
    )

    prompt = f"""
You are a professional ATS Resume Writer.

Rewrite the following resume professionally.

Requirements:

- Improve grammar.
- Improve formatting.
- Write a strong Professional Summary.
- Improve bullet points.
- Keep all factual information.
- Do not invent experience.
- Return ONLY Markdown.

Resume:

{resume_text}
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    result = response.choices[0].message.content

    return result


def generate_cover_letter(
    resume_text: str,
    job_description: str,
):
    model = os.getenv(
        "OPENAI_MODEL",
        "gpt-5-mini",
    )

    prompt = f"""
Write a professional cover letter.

Resume:

{resume_text}

Job Description:

{job_description}

Return only the cover letter.
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    result = response.choices[0].message.content

    return result
