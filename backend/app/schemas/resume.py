from pydantic import BaseModel


class ResumeAnalysis(BaseModel):
    score: int
    match_score: int

    strengths: list[str]
    weaknesses: list[str]

    matching_skills: list[str]
    missing_skills: list[str]

    suggestions: list[str]


class ResumeUploadResponse(BaseModel):
    filename: str
    pages: int
    analysis: ResumeAnalysis