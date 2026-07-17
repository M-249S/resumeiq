from app.services.openai_service import analyze_resume

result = analyze_resume(
    resume_text="""
Python Developer

Skills:
Python
FastAPI
PostgreSQL
Docker
Git
REST API
""",
    job_description="""
We are looking for a Backend Python Developer.

Requirements:

- Python
- FastAPI
- Docker
- PostgreSQL
- Redis
- AWS
- Git
"""
)

print(result)