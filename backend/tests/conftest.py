"""
Sets required environment variables before any app module is imported.
The app reads DATABASE_URL and SECRET_KEY at import time (module-level
os.getenv calls in app/db/session.py and app/auth/security.py), so these
must exist before pytest collects test files that import `app.main`.

DATABASE_URL only needs to be a syntactically valid SQLAlchemy URL —
create_engine() is lazy and doesn't actually connect until a query runs,
so no real Postgres instance is required for these tests.
"""
import os

os.environ.setdefault(
    "DATABASE_URL", "postgresql+psycopg://test:test@localhost/test"
)
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-ci-only-do-not-use-in-prod")
