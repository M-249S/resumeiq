import os

from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address


def client_key(request: Request) -> str:
    """
    Identify the caller for rate limiting.

    Behind a reverse proxy (Render, Vercel, ...) the socket address is the
    proxy's, so every visitor would share one bucket. With
    TRUST_PROXY_HEADERS=1 the left-most X-Forwarded-For entry (the original
    client) is used instead. That header can be forged by a client that
    reaches the app directly, so it is off by default and only meant for
    deployments where the platform's proxy is the sole way in. Abuse is
    still bounded by the demo's global daily budget.
    """
    if os.getenv("TRUST_PROXY_HEADERS") == "1":
        forwarded = request.headers.get("x-forwarded-for", "")
        first = forwarded.split(",")[0].strip()
        if first:
            return first
    return get_remote_address(request)


# Single shared limiter instance used by both the FastAPI app (main.py)
# and any router that wants to rate-limit specific endpoints.
limiter = Limiter(key_func=client_key)
