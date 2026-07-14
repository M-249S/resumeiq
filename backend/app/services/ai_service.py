def analyze_resume(text: str) -> dict:
    return {
        "score": 82,
        "strengths": [
            "Strong Python skills",
            "Experience with FastAPI",
            "Good backend development knowledge"
        ],
        "weaknesses": [
            "No professional summary",
            "Achievements are not quantified",
            "Missing LinkedIn profile"
        ],
        "missing_skills": [
            "Docker",
            "CI/CD",
            "Testing"
        ],
        "suggestions": [
            "Add a professional summary.",
            "Include measurable achievements.",
            "Add links to GitHub and LinkedIn."
        ]
    }