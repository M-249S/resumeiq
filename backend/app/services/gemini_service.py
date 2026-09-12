import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from app.prompts.analysis_prompt import ANALYSIS_PROMPT
from app.prompts.rewrite_prompt import REWRITE_PROMPT
from app.utils.markdown_utils import clean_markdown
from app.services.ai_client import generate

load_dotenv()

_openrouter = None


def _get_openrouter_client() -> OpenAI:
    global _openrouter

    if _openrouter is None:
        _openrouter = OpenAI(
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1",
        )

    return _openrouter


def analyze_resume(
    resume_text: str,
    job_description: str = "",
):
    prompt = ANALYSIS_PROMPT.replace("{resume_text}", resume_text).replace(
        "{job_description}", job_description or "N/A"
    )

    text = generate(prompt).strip()
    if text.startswith("```json"):
        text = text[7:]

    if text.endswith("```"):
        text = text[:-3]

    text = text.strip()

    try:
        return json.loads(text)

    except json.JSONDecodeError:
        raise ValueError(
            f"Gemini returned invalid JSON:\n{text}"
        )


def rewrite_resume(
    resume_text: str,
):
    prompt = REWRITE_PROMPT.replace(
        "{resume_text}",
        resume_text,
    )

    # -----------------------------
    # Gemini
    # -----------------------------
    try:

        text = generate(prompt).strip()
        if text.startswith("```markdown"):
            text = text[12:]

        elif text.startswith("```"):
            text = text[3:]

        if text.endswith("```"):
            text = text[:-3]

        text = clean_markdown(text)

        return text

    except Exception:
        pass

    # -----------------------------
    # OpenRouter
    # -----------------------------
    try:

        model = os.getenv(
            "OPENROUTER_MODEL",
            "google/gemma-4-26b-a4b-it:free",
        )

        response = _get_openrouter_client().chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        text = response.choices[0].message.content

        text = clean_markdown(text)

        return text

    except Exception:
        pass

    # -----------------------------
    # ERROR
    # -----------------------------

    raise RuntimeError(
            "AI provider unavailable. Please try again later."
        )
