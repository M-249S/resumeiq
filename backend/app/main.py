from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.health import router as health_router
from app.routers.resume import router as resume_router

app = FastAPI(
    title="AI Resume Optimizer API",
    description="Backend API for AI Resume Optimizer",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(resume_router)


@app.get("/")
def root():
    return {
        "message": "Welcome to AI Resume Optimizer"
    }