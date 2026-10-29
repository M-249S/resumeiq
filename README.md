# ResumeIQ

[![Backend CI](https://github.com/M-249S/ai-resume-optimizer/actions/workflows/backend-ci.yml/badge.svg)](https://github.com/M-249S/ai-resume-optimizer/actions/workflows/backend-ci.yml)

AI-powered ATS resume analyzer and optimizer. Upload a PDF resume (and optionally a job description) to get an ATS score, a job-match score, strengths and weaknesses, missing keywords, an AI-rewritten resume, and a tailored cover letter. Every analysis is saved to a per-user history.

**Live demo:** https://resumeiq-beta-ten.vercel.app

> The backend runs on a free Render instance, so the first request after a period of inactivity can take about a minute while the service wakes up.

---

## Features

- **ATS analysis**: overall score, job-match score, and per-category scores (formatting, keywords, experience, skills, education, readability)
- **Keyword match**: which job-description keywords the resume covers and which are missing
- **Strengths, weaknesses and suggestions** specific to the resume
- **AI resume rewrite**: download an improved resume as PDF
- **AI cover letter** tailored to the job description: plain-text output, editable in the browser, downloadable as `.docx`
- **Analysis history**: list, reopen and delete past analyses
- **Accounts**: registration and login with JWT authentication
- **Resilient AI layer**: retries on rate limits, optional fallback models, and a clean "try again" response instead of a crash

---

## Architecture

```
┌────────────────────┐   HTTPS / JSON   ┌────────────────────┐        ┌───────────────┐
│  React + TypeScript│ ───────────────▶ │  FastAPI backend   │ ─────▶ │  PostgreSQL   │
│  (Vercel)          │                  │  (Docker, Render)  │        │  (Render)     │
└────────────────────┘                  └─────────┬──────────┘        └───────────────┘
                                                  │
                                                  ▼
                                        OpenRouter (OpenAI-compatible API)
```

---

## Tech stack

**Backend**
- Python 3.12, FastAPI, Pydantic
- SQLAlchemy 2, Alembic migrations, PostgreSQL (psycopg 3)
- JWT authentication (python-jose, passlib/bcrypt)
- slowapi rate limiting on the AI endpoints
- AI via OpenRouter using the `openai` SDK
- PyPDF (PDF parsing), ReportLab (PDF output), python-docx (cover letter `.docx`)

**Frontend**
- React 19, TypeScript, Vite
- Tailwind CSS 4, Framer Motion
- React Router, Zustand, Axios
- oxlint

**DevSecOps**
- Docker image running as a non-root user, with a health check
- Deployed with a Render Blueprint (`render.yaml`): web service plus managed Postgres
- GitHub Actions CI, Dependabot for dependency updates (details below)

---

## CI/CD and security

Every push and pull request runs `.github/workflows/backend-ci.yml`:

| Job | What it checks |
|---|---|
| Lint | flake8 |
| Test | pytest |
| SAST | Bandit (medium severity and above) |
| Secret scan | Gitleaks |
| Dependency scan | Trivy filesystem scan of the pinned Python dependencies |
| Docker build and scan | Builds the image and scans it with Trivy |

Other practices:
- Dependencies are pinned, and Dependabot opens grouped weekly update PRs for pip, npm, Docker and GitHub Actions. Each PR must pass the full pipeline before merging.
- Secrets are never committed. They are supplied through environment variables and the Render dashboard.
- AI endpoints are rate limited, and CORS is an explicit allowlist.
- Database schema changes go through Alembic migrations, applied automatically on container start.

---

## Project structure

```
backend/
  app/
    auth/         # JWT, register/login, current-user dependency
    routers/      # health, resume, users
    services/     # AI client, analysis, cover letter, PDF/DOCX
    models/ db/   # SQLAlchemy models and session
    schemas/      # Pydantic schemas
  alembic/        # database migrations
  tests/          # pytest suite
  Dockerfile
  DEPLOY.md       # Render deployment notes
frontend/
  src/            # pages, components, services, state
render.yaml       # Render Blueprint (backend + Postgres)
.github/          # CI workflow and Dependabot config
```

---

## API overview

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/auth/register` | Create an account |
| POST | `/auth/login` | Log in (OAuth2 password form), returns a JWT |
| GET | `/auth/me` | Current user |
| POST | `/resume/upload` | Analyze a PDF resume (optional job description) |
| POST | `/resume/improve` | AI-rewritten resume |
| POST | `/resume/download` | Download the improved resume as PDF |
| POST | `/resume/cover-letter` | Generate a cover letter |
| POST | `/resume/cover-letter/download` | Download the cover letter as `.docx` |
| GET | `/resume/history` | List your past analyses (`limit`, `offset`) |
| GET | `/resume/history/{id}` | Full details of one analysis |
| DELETE | `/resume/history/{id}` | Delete one analysis |

Interactive docs are served at `/docs` when running the backend.

---

## Run locally

**Prerequisites:** Python 3.12, Node.js, and a PostgreSQL database.

### Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate    macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env        # then fill in real values
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Set `VITE_API_URL` to the backend URL (for example `http://localhost:8000`) if it is not already configured.

### Tests and lint

```bash
cd backend
pytest -q
flake8 app/ tests/ --max-line-length=100 --extend-ignore=E501
bandit -r app/ -f screen --severity-level medium
```

---

## Configuration

Backend environment variables (see `backend/.env.example`):

| Variable | Required | Purpose |
|---|---|---|
| `DATABASE_URL` | yes | PostgreSQL connection string (a bare `postgresql://` URL is accepted) |
| `SECRET_KEY` | yes | Signs JWT tokens |
| `CORS_ORIGINS` | yes (production) | Comma-separated list of allowed frontend origins |
| `OPENROUTER_API_KEY` | for real AI output | OpenRouter API key |
| `OPENROUTER_MODEL` | no | Primary model |
| `OPENROUTER_FALLBACK_MODELS` | no | Comma-separated models to try if the primary keeps failing |
| `OPENROUTER_RETRIES` | no | Attempts per model (default 2) |

Without an AI key the analysis falls back to a simple built-in heuristic so the app still runs, but cover letters need a working AI provider. Deployment steps are in [`backend/DEPLOY.md`](backend/DEPLOY.md).

---

## Roadmap

- [x] Resume analysis, rewrite and cover letter generation
- [x] JWT authentication
- [x] PostgreSQL and Alembic migrations
- [x] Analysis history
- [x] Docker, CI/CD pipeline and security scanning
- [x] Deployment (Render and Vercel)
- [ ] Frontend tests and a frontend CI job
- [ ] Backend deployment to a paid tier (persistent database, no cold starts)

---

## Author

**Mujahid Suliman Hamid Adam**
Software Engineer, MSc Information Technology

## License

MIT License
