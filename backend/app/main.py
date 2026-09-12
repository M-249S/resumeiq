import os

from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.limiter import limiter
from app.routers.health import router as health_router
from app.routers.resume import router as resume_router
from app.routers.users import router as users_router
from app.auth.router import router as auth_router

load_dotenv()

app = FastAPI(
    title="ResumeIQ API",
    description="AI-powered ATS Resume Analysis & Resume Optimization Platform.",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# Rate limiting
# Protects the paid-AI-backed resume endpoints from abuse. Limits are set
# per-route with @limiter.limit(...) (see app/routers/resume.py).
# ---------------------------------------------------------------------------
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ---------------------------------------------------------------------------
# CORS
# Origins come from the CORS_ORIGINS env var (comma-separated), falling
# back to the local dev servers so `npm run dev` keeps working out of
# the box. Add your production frontend URL to CORS_ORIGINS when deploying.
# ---------------------------------------------------------------------------
default_origins = "http://localhost:5173,http://localhost:5174"
origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", default_origins).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(resume_router)
app.include_router(auth_router)
app.include_router(users_router)


@app.get("/")
def root():
    return {"message": "Welcome to ResumeIQ API"}
