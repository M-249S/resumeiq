import os
import secrets

from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from sqlalchemy.orm import Session

from app.models.user import User

from app.auth.schemas import (
    UserRegister,
)

from app.auth.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
)


def get_user_by_email(
    db: Session,
    email: str,
):
    return (
        db.query(User)
        .filter(User.email == email)
        .first()
    )


def register_user(
    db: Session,
    user: UserRegister,
):
    existing_user = get_user_by_email(
        db,
        user.email,
    )

    if existing_user:
        raise ValueError(
            "Email already registered."
        )

    new_user = User(
        full_name=user.full_name,
        email=user.email,
        hashed_password=hash_password(
            user.password
        ),
    )

    db.add(new_user)

    db.commit()

    db.refresh(new_user)

    return new_user


def login_user(
    db: Session,
    email: str,
    password: str,
):
    db_user = get_user_by_email(
        db,
        email,
    )

    if not db_user:
        raise ValueError(
            "Invalid email or password."
        )

    if not verify_password(
        password,
        db_user.hashed_password,
    ):
        raise ValueError(
            "Invalid email or password."
        )

    access_token = create_access_token(
        {
            "sub": str(db_user.id),
        }
    )

    refresh_token = create_refresh_token(
        {
            "sub": str(db_user.id),
        }
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


class GoogleNotConfiguredError(RuntimeError):
    """GOOGLE_CLIENT_ID is not set on the server."""


def _issue_tokens(user: User) -> dict:
    return {
        "access_token": create_access_token({"sub": str(user.id)}),
        "refresh_token": create_refresh_token({"sub": str(user.id)}),
        "token_type": "bearer",
    }


def verify_google_credential(credential: str) -> dict:
    """Validate a Google ID token (signature, expiry, audience) and return its claims."""
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    if not client_id:
        raise GoogleNotConfiguredError("Google sign-in is not configured.")

    try:
        return google_id_token.verify_oauth2_token(
            credential,
            google_requests.Request(),
            client_id,
        )
    except ValueError as exc:
        raise ValueError("Invalid Google credential.") from exc


def login_with_google(db: Session, credential: str) -> dict:
    claims = verify_google_credential(credential)

    # Only trust the email if Google itself has verified it. Without this,
    # an attacker could claim someone else's address and take over the account.
    if not claims.get("email_verified"):
        raise ValueError("Google account email is not verified.")

    sub = claims["sub"]
    email = claims["email"].lower()

    user = db.query(User).filter(User.google_sub == sub).first()

    if user is None:
        user = get_user_by_email(db, email)
        if user is not None:
            # Existing password account with the same verified email: link it.
            user.google_sub = sub
        else:
            user = User(
                full_name=(claims.get("name") or email.split("@")[0])[:100],
                email=email,
                # Google users have no password. Store an unguessable one so
                # the NOT NULL column stays valid and password login can't match.
                hashed_password=hash_password(secrets.token_urlsafe(32)),
                google_sub=sub,
            )
            db.add(user)
        db.commit()
        db.refresh(user)

    if not user.is_active:
        raise ValueError("Account is disabled.")

    return _issue_tokens(user)
