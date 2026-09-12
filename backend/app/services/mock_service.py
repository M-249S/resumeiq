import re


def extract_keywords(text: str) -> set:
    words = re.findall(r"[A-Za-z+#.]+", text.lower())

    stop_words = {
        "the",
        "and",
        "with",
        "for",
        "your",
        "you",
        "are",
        "this",
        "that",
        "from",
        "into",
        "have",
        "will",
        "our",
        "their",
        "using",
        "years",
        "year",
        "experience",
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
        match_score = int(
            len(matching) / len(job_keywords) * 100
        )
    else:
        match_score = 0

    # -------------------------
    # Dynamic Overall Score
    # -------------------------

    score = 60
    score += len(matching) * 4
    score -= len(missing) * 2
    score = max(35, min(score, 100))

    # -------------------------
    # ATS Level
    # -------------------------

    if match_score >= 85:
        ats_level = "Excellent"
    elif match_score >= 65:
        ats_level = "Good"
    elif match_score >= 40:
        ats_level = "Average"
    else:
        ats_level = "Poor"

    # -------------------------
    # Dimension Scores
    # -------------------------

    formatting_score = 90

    keyword_score = (
        match_score if job_keywords else 60
    )

    experience_score = min(
        100,
        60 + len(matching) * 3,
    )

    skills_score = min(
        100,
        55 + len(matching) * 4,
    )

    education_score = 85

    readability_score = 88

    # -------------------------
    # Strengths
    # -------------------------

    strengths = []

    if "python" in resume_keywords:
        strengths.append("Strong Python skills")

    if "fastapi" in resume_keywords:
        strengths.append("Experience with FastAPI")

    if "docker" in resume_keywords:
        strengths.append("Docker knowledge")

    if "sql" in resume_keywords:
        strengths.append("Database experience")

    if "git" in resume_keywords:
        strengths.append("Version control with Git")

    if not strengths:
        strengths.append("Relevant technical background")

    # -------------------------
    # Weaknesses
    # -------------------------

    weaknesses = []

    if "linkedin" not in resume_text.lower():
        weaknesses.append("Missing LinkedIn profile")

    if "github" not in resume_text.lower():
        weaknesses.append("Missing GitHub portfolio")

    if len(resume_text) < 1200:
        weaknesses.append("Resume could include more details")

    if len(missing) > 5:
        weaknesses.append(
            "Several important job keywords are missing"
        )

    if not weaknesses:
        weaknesses.append(
            "Resume is generally well optimized"
        )

    # -------------------------
    # Suggestions
    # -------------------------

    suggestions = []

    if missing:
        suggestions.append(
            "Add missing technical skills relevant to the job."
        )

    suggestions.append(
        "Include measurable achievements."
    )

    suggestions.append(
        "Add a professional summary."
    )

    suggestions.append(
        "Include GitHub and LinkedIn profile links."
    )

    # -------------------------
    # Summary
    # -------------------------

    summary = (
        f"This resume has an overall ATS score of {score}/100 "
        f"with a job match score of {match_score}%. "
        f"The biggest opportunity for improvement is adding "
        f"missing keywords and measurable achievements."
    )

    return {
        "score": score,
        "match_score": match_score,
        "ats_level": ats_level,
        "summary": summary,
        "formatting_score": formatting_score,
        "keyword_score": keyword_score,
        "experience_score": experience_score,
        "skills_score": skills_score,
        "education_score": education_score,
        "readability_score": readability_score,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "matching_skills": matching,
        "missing_skills": missing,
        "suggestions": suggestions,
    }


def rewrite_resume(
    resume_text: str,
):
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
