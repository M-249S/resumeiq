from fastapi import FastAPI

from app.routers.health import router as health_router

app = FastAPI(
    title="AI Resume Optimizer API",
    description="Backend API for AI Resume Optimizer",
    version="1.0.0",
)


app.include_router(health_router)


@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Welcome to AI Resume Optimizer "
    }