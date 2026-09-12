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
