# Deploying to Render

The backend already targets Postgres (`DATABASE_URL=postgresql+psycopg://...`
in `.env.example`, `psycopg[binary]` in `requirements.txt`, Alembic
migrations in `alembic/versions/`) — this doc covers what's specific to
Render on top of that.

## What changed to make this Render-ready

1. **`Dockerfile` now binds to `$PORT`, not a hard-coded 8000.**
   Render assigns the port your container must listen on via the `PORT`
   env var (defaulting to 10000 if you don't set one yourself). The CMD
   is now `uvicorn ... --port ${PORT:-8000}`, so it works whether Render
   sets `PORT` or not, and local `docker run` without it still falls
   back to 8000.

2. **`app/db/session.py` normalizes the database URL.** Render's
   `fromDatabase` connection string uses the bare `postgresql://` scheme
   (the psycopg2 dialect). This project installs **psycopg 3**, which
   SQLAlchemy only picks correctly if the URL says
   `postgresql+psycopg://`. `_normalize_database_url()` rewrites the
   scheme automatically, so you can paste Render's connection string
   as-is — no manual edit. `alembic/env.py` reuses the same function so
   migrations and the running app always agree on how to connect.
   Verified locally against a real Postgres 16 instance with both a
   bare `postgresql://` URL and a `+psycopg` one — both work.

3. **`render.yaml`** (repo root) is a Render Blueprint: one file that
   provisions the web service *and* its Postgres database together,
   wires `DATABASE_URL` between them automatically, and generates
   `SECRET_KEY` for you. This is optional — you can also click through
   the dashboard manually (steps below) — but it means the whole setup
   is reproducible from the repo instead of living only in Render's UI.

## Option A — deploy via Blueprint (recommended)

1. Push these changes to GitHub first.
2. In the Render dashboard: **New -> Blueprint**, pick this repo.
   Render reads `render.yaml` from the repo root and shows you the
   `resumeiq-backend` web service + `resumeiq-db` database it's about
   to create.
3. Click **Apply**. Render creates the Postgres database first, then
   builds and deploys the web service, wiring `DATABASE_URL` from the
   database into the service automatically.
4. Once it's live, open the service's **Environment** tab and fill in
   the variables marked `sync: false` in `render.yaml`:
   - `CORS_ORIGINS` — your deployed frontend's origin, e.g.
     `https://resumeiq.vercel.app` (comma-separate if there's more than
     one, e.g. a preview URL too)
   - `GEMINI_API_KEY` and/or `OPENROUTER_API_KEY` — at least one, or
     the app falls back to mock analysis data
5. Redeploy (or it picks up new env vars on the next deploy
   automatically, depending on your Render settings).

## Option B — deploy manually (no Blueprint)

1. **New -> PostgreSQL.** Name it, pick the **Free** plan, create it.
   Copy its **Internal Database URL** (same-region services should use
   the internal URL — it's faster and doesn't leave Render's network).
2. **New -> Web Service -> Docker.** Point it at this repo,
   `backend/Dockerfile` as the Dockerfile path, `backend` as the root
   directory.
3. Add environment variables on the service:
   | Key | Value |
   |---|---|
   | `DATABASE_URL` | the Postgres URL from step 1 (paste as-is — the app rewrites the scheme itself) |
   | `SECRET_KEY` | output of `python -c "import secrets; print(secrets.token_hex(32))"` |
   | `CORS_ORIGINS` | your frontend's deployed URL |
   | `GEMINI_API_KEY` / `OPENROUTER_API_KEY` | at least one |
4. Set **Health Check Path** to `/health` in the service settings.
5. Deploy.

## Verifying it worked

```bash
curl https://<your-service>.onrender.com/health
# {"status":"good"}

curl -X POST https://<your-service>.onrender.com/auth/register \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Test","email":"test@example.com","password":"SuperSecret123!"}'
```

If registration returns a user object, the app reached Postgres and
Alembic's migrations ran (the Dockerfile runs `alembic upgrade head`
before starting uvicorn on every boot, so a fresh deploy always has an
up-to-date schema).

## Free-tier things worth knowing before you rely on this

- **Free Postgres expires.** Render's free database becomes
  inaccessible 30 days after creation, then is deleted ~14 days after
  that if you haven't upgraded. There's no backup to restore from on
  the free plan. Render emails you before both deadlines. Fine for a
  portfolio demo; set a reminder, or upgrade the DB plan, if you want
  this to keep working past a month.
- **Free web services sleep.** After 15 minutes with no traffic, the
  service spins down; the next request wakes it, which takes about a
  minute (the visitor sees a Render loading page meanwhile). This is
  why a demo link can feel slow on the first hit after a while — not a
  bug.
- **CORS_ORIGINS must be exact.** It's an exact-match allowlist, not a
  wildcard — `https://resumeiq.vercel.app` and
  `https://resumeiq-git-main.vercel.app` are different origins if you
  use preview deployments too.
