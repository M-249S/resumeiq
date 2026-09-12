from jose import jwt

from app.auth.security import (
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)


def test_hash_password_does_not_return_plaintext():
    hashed = hash_password("SuperSecret123!")
    assert hashed != "SuperSecret123!"


def test_verify_password_accepts_correct_password():
    hashed = hash_password("SuperSecret123!")
    assert verify_password("SuperSecret123!", hashed) is True


def test_verify_password_rejects_wrong_password():
    hashed = hash_password("SuperSecret123!")
    assert verify_password("something-else", hashed) is False


def test_access_token_has_access_type_claim():
    token = create_access_token({"sub": "user@example.com"})
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["type"] == "access"
    assert payload["sub"] == "user@example.com"


def test_refresh_token_has_refresh_type_claim():
    token = create_refresh_token({"sub": "user@example.com"})
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["type"] == "refresh"


def test_access_and_refresh_tokens_are_distinguishable():
    # A refresh token must never be accepted where an access token is
    # expected, or vice versa — this is what makes that check possible.
    access = create_access_token({"sub": "user@example.com"})
    refresh = create_refresh_token({"sub": "user@example.com"})

    access_payload = jwt.decode(access, SECRET_KEY, algorithms=[ALGORITHM])
    refresh_payload = jwt.decode(refresh, SECRET_KEY, algorithms=[ALGORITHM])

    assert access_payload["type"] != refresh_payload["type"]
