from pydantic import BaseModel


class ResumeAnalysis(BaseModel):
    score: int
    match_score: int

    ats_level: str
    summary: str

    formatting_score: int
    keyword_score: int
    experience_score: int
    skills_score: int
    education_score: int
    readability_score: int

    strengths: list[str]
    weaknesses: list[str]

    matching_skills: list[str]
    missing_skills: list[str]

    suggestions: list[str]


class ResumeUploadResponse(BaseModel):
    filename: str
    pages: int
    analysis: ResumeAnalysis
