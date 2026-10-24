
from dotenv import load_dotenv

from app.services.ai_client import generate
from app.utils.markdown_utils import clean_markdown, strip_inline_markdown

load_dotenv()


def generate_cover_letter(
    resume_text: str,
    job_description: str,
):
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

Return ONLY the cover letter as plain text. Do NOT use Markdown formatting
(no asterisks, no bold, no headings).

Resume:

{resume_text}

Job Description:

{job_description}
"""

    text = generate(prompt).strip()

    if text.startswith("```markdown"):
        text = text[12:]

    elif text.startswith("```"):
        text = text[3:]

    if text.endswith("```"):
        text = text[:-3]

    return strip_inline_markdown(clean_markdown(text))
