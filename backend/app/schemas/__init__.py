from .auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
)

from .user import UserResponse

# Re-exported for convenience (e.g. `from app.schemas import TokenResponse`)
# rather than reaching into the submodule directly. flake8 would otherwise
# flag these as unused imports since nothing in this file references them.
__all__ = [
    "RegisterRequest",
    "LoginRequest",
    "TokenResponse",
    "UserResponse",
]
