FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Apply latest OS security patches before installing anything else — base
# image packages can lag behind upstream CVE fixes between image builds.
# System deps below are needed by psycopg (Postgres driver) and reportlab.
RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create a non-root user and switch to it before running the app.
RUN groupadd -r appuser && useradd -r -g appuser appuser \
    && chown -R appuser:appuser /app
USER appuser

# Render (and most container hosts) assign the listen port at runtime via
# $PORT rather than letting the image hard-code one — EXPOSE 8000 below is
# just documentation/local-default, the CMD actually binds to $PORT.
EXPOSE 8000
ENV PORT=8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f "http://localhost:${PORT:-8000}/health" || exit 1

# alembic upgrade head runs on every container start, so a fresh Render
# deploy (or a new migration file added later) always lands on a
# schema that matches the code — no separate manual migration step.
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
