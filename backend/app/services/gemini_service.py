import json
import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def analyze_resume(
    resume_text: str,
    job_description: str = "",
):

    model = os.getenv(
        "GEMINI_MODEL",
        "models/gemini-3.5-flash",
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

    response = client.models.generate_content(
        model=model,
        contents=prompt,
    )

    text = response.text.strip()

    if text.startswith("```json"):
        text = text[7:]

    if text.endswith("```"):
        text = text[:-3]

    text = text.strip()

    print("\n========== Gemini Analysis ==========\n")
    print(text)
    print("\n=====================================\n")

    return json.loads(text)


def rewrite_resume(
    resume_text: str,
):
    model = os.getenv(
        "GEMINI_MODEL",
        "models/gemini-3.5-flash",
    )

    prompt = f"""
You are a world-class Senior Resume Writer and ATS Optimization Expert.

Your task is to rewrite the resume into a modern, ATS-friendly resume.

Rules:

- Keep ALL factual information.
- Never invent work experience.
- Never invent certifications.
- Never invent education.
- Never invent skills the candidate doesn't have.
- Improve grammar and wording.
- Improve formatting.
- Make the resume ATS-friendly.
- Use concise and professional language.
- Keep the resume to 1-2 pages.
- Use Markdown formatting.

The resume should contain these sections if applicable:

# Full Name
## Professional Summary
## Technical Skills
## Projects
## Professional Experience
## Education
## Certifications
## Languages

If the resume does NOT contain any projects,
create a section named:

## Suggested Projects

Recommend exactly 3 portfolio projects that would strengthen the candidate's resume.

Each project should contain:

- Project Name
- Short Description
- Technologies

Clearly mention that these are recommended portfolio projects and NOT existing experience.

Do not invent professional experience.

Return ONLY the rewritten resume in Markdown.

Resume:

{resume_text}
"""

    response = client.models.generate_content(
        model=model,
        contents=prompt,
    )

    text = response.text.strip()

    if text.startswith("```markdown"):
        text = text[12:]

    elif text.startswith("```"):
        text = text[3:]

    if text.endswith("```"):
        text = text[:-3]

    text = text.strip()

    print("\n========== Rewritten Resume ==========\n")
    print(text)
    print("\n======================================\n")

    return text