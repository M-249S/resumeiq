from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict


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


class ResumeHistoryItem(BaseModel):
    """
    Lightweight summary row for the history list. The full `analysis`
    payload is deliberately left out here so listing many records stays
    cheap — fetch /resume/history/{id} for the complete breakdown.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    score: int
    match_score: int
    created_at: datetime


class ResumeHistoryDetail(BaseModel):
    """Single past analysis, including the full stored `analysis` JSON."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    score: int
    match_score: int
    analysis: ResumeAnalysis
    created_at: datetime
