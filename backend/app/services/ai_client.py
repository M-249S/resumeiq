import logging
import os
import time

from dotenv import load_dotenv
from openai import (
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    InternalServerError,
    OpenAI,
    RateLimitError,
)

load_dotenv()

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "google/gemma-4-26b-a4b-it:free"

# Errors worth retrying: the free OpenRouter models are shared and get
# rate-limited (429) or time out regularly. Anything else (bad request,
# auth, etc.) will not fix itself by waiting.
_TRANSIENT_ERRORS = (
    RateLimitError,
    APIConnectionError,
    APITimeoutError,
    InternalServerError,
)

_client = None


class AIUnavailableError(RuntimeError):
    """
    Raised when no AI model could produce a response (all retries and
    fallback models exhausted, or the provider is misconfigured).

    Routers turn this into a clean HTTP 503 so the frontend can show a
    friendly "try again" message instead of a crash.
    """


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
            raise AIUnavailableError("OPENROUTER_API_KEY is not set.")

        _client = OpenAI(
            api_key=api_key.strip(),
            base_url="https://openrouter.ai/api/v1",
        )

    return _client


def get_models() -> list[str]:
    """
    Models to try, in order: OPENROUTER_MODEL first, then every model in
    OPENROUTER_FALLBACK_MODELS (comma-separated). Duplicates are dropped.
    Read from the environment on each call so a changed env var takes
    effect without a code change.
    """
    primary = os.getenv("OPENROUTER_MODEL", DEFAULT_MODEL).strip()
    fallbacks = os.getenv("OPENROUTER_FALLBACK_MODELS", "")

    models: list[str] = []

    for name in [primary, *fallbacks.split(",")]:
        name = name.strip()

        if name and name not in models:
            models.append(name)

    return models


def _int_env(name: str, default: int) -> int:
    try:
        return max(int(os.getenv(name, default)), 1)
    except (TypeError, ValueError):
        return default


def generate(
    prompt: str,
    temperature: float = 0.4,
    timeout: float | None = None,
) -> str:
    """
    Send `prompt` to OpenRouter and return the reply text.

    Each model gets OPENROUTER_RETRIES attempts (default 2) with a short
    backoff on transient errors (429, timeouts, connection/5xx). If a
    model keeps failing, the next one in OPENROUTER_FALLBACK_MODELS is
    tried. Raises AIUnavailableError if everything fails.
    """
    client = _get_client()
    attempts = _int_env("OPENROUTER_RETRIES", 2)
    backoff = float(os.getenv("OPENROUTER_RETRY_DELAY", "2"))

    last_error: Exception | None = None

    for model in get_models():
        for attempt in range(1, attempts + 1):
            try:
                kwargs = {}

                if timeout is not None:
                    kwargs["timeout"] = timeout

                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    **kwargs,
                )

                content = response.choices[0].message.content

                if content and content.strip():
                    return content

                last_error = ValueError("empty response")
                logger.warning(
                    "AI model %s returned an empty reply (attempt %d/%d)",
                    model,
                    attempt,
                    attempts,
                )

            except AuthenticationError as exc:
                # A bad key never recovers by retrying or switching model.
                logger.error("OpenRouter rejected the API key: %s", exc)
                raise AIUnavailableError(
                    "AI provider rejected the API key."
                ) from exc

            except _TRANSIENT_ERRORS as exc:
                last_error = exc
                logger.warning(
                    "AI model %s failed (attempt %d/%d): %s",
                    model,
                    attempt,
                    attempts,
                    exc,
                )

            except Exception as exc:
                # Non-transient error for this model (e.g. model removed,
                # bad request): skip its remaining attempts, try the next.
                last_error = exc
                logger.warning("AI model %s failed: %s", model, exc)
                break

            if attempt < attempts:
                time.sleep(backoff * attempt)

    raise AIUnavailableError(
        "The AI service is busy right now. Please try again in a minute."
    ) from last_error
