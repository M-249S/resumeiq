import os

from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()


def _normalize_database_url(url: str) -> str:
    """
    Most managed Postgres providers (Render's included) hand you a bare
    `postgresql://...` connection string, which is the psycopg2 dialect.
    This project installs psycopg 3 instead, so SQLAlchemy needs the
    `+psycopg` driver suffix or it tries (and fails) to import psycopg2.
    Rewriting it here means any DATABASE_URL — local, Docker Compose, or
    whatever a host injects — works without hand-editing it first.
    """
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


_raw_database_url = os.getenv("DATABASE_URL")

if not _raw_database_url:
    raise RuntimeError(
        "DATABASE_URL is not set. Copy .env.example to .env locally, or "
        "set DATABASE_URL in your host's environment variables."
    )

DATABASE_URL = _normalize_database_url(_raw_database_url)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
