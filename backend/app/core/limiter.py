from slowapi import Limiter
from slowapi.util import get_remote_address

# Single shared limiter instance used by both the FastAPI app (main.py)
# and any router that wants to rate-limit specific endpoints.
limiter = Limiter(key_func=get_remote_address)
