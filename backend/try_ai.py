import os
from dotenv import load_dotenv

load_dotenv()
print("OPENROUTER key set:", bool(os.getenv("OPENROUTER_API_KEY")))
print("Model:", os.getenv("OPENROUTER_MODEL"))

from app.services.cover_letter_service import generate_cover_letter

resume = """Omer Ali. Junior DevOps engineer.
Skills: Docker, GitHub Actions, Terraform, Python, Flask, Linux.
Projects: CI/CD pipeline with security scanning; AWS EC2 deployment with Terraform."""

job = "Junior DevOps Engineer. Requirements: Docker, CI/CD, Terraform, AWS, Linux."

print("\n--- COVER LETTER ---\n")
print(generate_cover_letter(resume, job))
