import re


def extract_keywords(text: str) -> set:
    words = re.findall(r"[A-Za-z+#.]+", text.lower())

    stop_words = {
        "the", "and", "with", "for", "your", "you",
        "are", "this", "that", "from", "into",
        "have", "will", "our", "their", "using",
        "years", "year", "experience"
    }

    return {
        word
        for word in words
        if len(word) > 2 and word not in stop_words
    }


def analyze_resume(
    resume_text: str,
    job_description: str = "",
):

    resume_keywords = extract_keywords(resume_text)
    job_keywords = extract_keywords(job_description)

    matching = sorted(resume_keywords & job_keywords)
    missing = sorted(job_keywords - resume_keywords)

    if job_keywords:
        match_score = int(len(matching) / len(job_keywords) * 100)
    else:
        match_score = 0

    return {
        "score": 82,
        "match_score": match_score,
        "strengths": [
            "Strong Python skills",
            "Experience with FastAPI",
            "Good backend development knowledge",
        ],
        "weaknesses": [
            "No professional summary",
            "Achievements are not quantified",
            "Missing LinkedIn profile",
        ],
        "matching_skills": matching,
        "missing_skills": missing,
        "suggestions": [
            "Add a professional summary.",
            "Include measurable achievements.",
            "Add links to GitHub and LinkedIn.",
        ],
    }


def rewrite_resume(
    resume_text: str,
):
    """
    Mock implementation used when no AI provider is available.
    """

    return f"""# Professional Summary

Experienced software developer with strong problem-solving skills and a passion for backend development and Artificial Intelligence.

# Skills

- Python
- FastAPI
- REST APIs
- SQL
- Git
- Docker

# Experience

{resume_text}

# Projects

- AI Resume Optimizer
- Backend API Development

# Education

(Keep your original education section.)
"""