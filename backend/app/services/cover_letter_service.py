import os

from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def generate_cover_letter(
    resume_text: str,
    job_description: str,
):
    model = os.getenv(
        "GEMINI_MODEL",
        "models/gemini-3.5-flash",
    )

    prompt = f"""
You are an expert career coach and professional resume writer.

Write a professional cover letter based on the candidate's resume and the job description.

Requirements:

- Professional tone.
- ATS friendly.
- One page maximum.
- Do NOT invent work experience.
- Highlight matching skills.
- Explain why the candidate fits the role.
- End with a professional closing.

Return ONLY the cover letter in Markdown.

Resume:

{resume_text}

Job Description:

{job_description}
"""

    response = client.models.generate_content(
        model=model,
        contents=prompt,
    )

    return response.text