import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

_client = None


def _get_client() -> OpenAI:
    """
    Lazily create the OpenRouter client.

    Creating the client at import time meant the whole app failed to
    start if OPENROUTER_API_KEY wasn't set yet, even though the app is
    designed to fall back to other providers/mock data. Building it on
    first use avoids that.
    """
    global _client

    if _client is None:
        api_key = os.getenv("OPENROUTER_API_KEY")

        if not api_key:
            raise RuntimeError("OPENROUTER_API_KEY is not set.")

        _client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
        )

    return _client


def generate(prompt: str) -> str:
    client = _get_client()

    response = client.chat.completions.create(
        model=os.getenv(
            "OPENROUTER_MODEL",
            "google/gemma-4-26b-a4b-it:free",
        ),
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        temperature=0.4,
    )

    return response.choices[0].message.content
