from io import BytesIO
from sqlalchemy.orm import Session

from fastapi import Depends
from fastapi import Query
from fastapi import Request

from app.core.limiter import limiter

from app.db.session import get_db
from app.auth.dependencies import get_current_user

from app.models.user import User
from app.resume.models import ResumeAnalysis
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import Response, StreamingResponse
from pypdf import PdfReader

from app.schemas.resume import (
    ResumeHistoryDetail,
    ResumeHistoryItem,
    ResumeUploadResponse,
)
from app.schemas.cover_letter import CoverLetterResponse

from app.services.ai_service import analyze_resume
from app.services.demo_budget import demo_budget
from app.services.ai_client import AIUnavailableError
from app.services.cover_letter_service import generate_cover_letter
from app.services.gemini_service import rewrite_resume
from app.services.pdf_service import generate_resume_pdf
from app.services.word_service import generate_cover_letter_docx
router = APIRouter()

# Per-IP limit for the AI-backed endpoints below. Each of these calls a
# paid AI provider, so they're limited to avoid runaway costs from a
# single client hammering the API.
AI_RATE_LIMIT = "5/minute"

# Limits for the unauthenticated demo endpoint. Stricter than the account
# limits above because anyone can call it: a tighter per-IP rate, small
# inputs, and a global daily budget (see app/services/demo_budget.py).
DEMO_RATE_LIMIT = "3/hour"
DEMO_MAX_BYTES = 2 * 1024 * 1024
DEMO_MAX_PAGES = 4
DEMO_MAX_RESUME_CHARS = 12000
DEMO_MAX_JOB_CHARS = 4000
AI_BUSY_MESSAGE = "The AI service is busy right now. Please try again in a minute."


def extract_text_from_pdf(pdf_bytes: bytes) -> tuple[str, int]:
    """
    Extract text from PDF.
    """

    reader = PdfReader(BytesIO(pdf_bytes))

    text = ""

    for page in reader.pages:
        extracted = page.extract_text()

        if extracted:
            text += extracted + "\n"

    return text, len(reader.pages)


@router.post(
    "/resume/upload",
    response_model=ResumeUploadResponse,
    tags=["Resume"],
)
@limiter.limit(AI_RATE_LIMIT)
async def upload_resume(
    request: Request,
    file: UploadFile = File(...),
    job_description: str = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed.",
        )

    pdf_bytes = await file.read()

    text, pages = extract_text_from_pdf(pdf_bytes)

    analysis = analyze_resume(
        resume_text=text,
        job_description=job_description,

    )
    if not analysis:
        raise HTTPException(
            status_code=500,
            detail="Resume analysis failed.",
        )
    resume_analysis = ResumeAnalysis(
        user_id=current_user.id,
        filename=file.filename or "resume.pdf",
        score=analysis.get("score", 0),
        match_score=analysis.get("match_score", 0),
        analysis=analysis,
    )

    db.add(resume_analysis)
    db.commit()
    db.refresh(resume_analysis)

    return {
        "filename": file.filename or "resume.pdf",
        "pages": pages,
        "analysis": analysis,
    }


@router.post(
    "/resume/demo",
    response_model=ResumeUploadResponse,
    tags=["Resume"],
)
@limiter.limit(DEMO_RATE_LIMIT)
async def demo_resume_analysis(
    request: Request,
    file: UploadFile = File(...),
    job_description: str = Form(""),
):
    """
    Analyze a resume without an account. Nothing is stored, and a failed AI
    call returns an error instead of mock data so guests never see fake
    results presented as real.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed.",
        )

    pdf_bytes = await file.read(DEMO_MAX_BYTES + 1)
    if len(pdf_bytes) > DEMO_MAX_BYTES:
        raise HTTPException(
            status_code=413,
            detail="That file is too large for the free demo. Please use a PDF under 2MB.",
        )

    try:
        text, pages = extract_text_from_pdf(pdf_bytes)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="We couldn't read that PDF. Please try a different file.",
        )

    if pages > DEMO_MAX_PAGES:
        raise HTTPException(
            status_code=400,
            detail=f"The free demo supports up to {DEMO_MAX_PAGES} pages. Create an account to analyze longer resumes.",
        )

    if not text.strip():
        raise HTTPException(
            status_code=400,
            detail="We couldn't find any text in that PDF. Scanned documents aren't supported.",
        )

    if not demo_budget.try_consume():
        raise HTTPException(
            status_code=429,
            detail="The free demo has reached its limit for today. Please try again tomorrow or create an account.",
        )

    analysis = analyze_resume(
        resume_text=text[:DEMO_MAX_RESUME_CHARS],
        job_description=job_description[:DEMO_MAX_JOB_CHARS],
        allow_mock=False,
    )
    if not analysis:
        demo_budget.refund()
        raise HTTPException(status_code=503, detail=AI_BUSY_MESSAGE)

    return {
        "filename": file.filename or "resume.pdf",
        "pages": pages,
        "analysis": analysis,
    }


@router.post(
    "/resume/improve",
    tags=["Resume"],
)
@limiter.limit(AI_RATE_LIMIT)
async def improve_resume(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed.",
        )

    pdf_bytes = await file.read()

    text, _ = extract_text_from_pdf(pdf_bytes)

    improved_resume = rewrite_resume(text)

    return {
        "resume": improved_resume,
    }


@router.post(
    "/resume/download",
    tags=["Resume"],
)
@limiter.limit(AI_RATE_LIMIT)
async def download_resume(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """
    Rewrite resume and return it as PDF.
    """

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed.",
        )

    pdf_bytes = await file.read()

    text, _ = extract_text_from_pdf(pdf_bytes)

    improved_resume = rewrite_resume(text)

    pdf_buffer = generate_resume_pdf(improved_resume)

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": 'attachment; filename="improved_resume.pdf"',
        },
    )


@router.post(
    "/resume/cover-letter",
    response_model=CoverLetterResponse,
    tags=["Resume"],
)
@limiter.limit(AI_RATE_LIMIT)
async def cover_letter(
    request: Request,
    file: UploadFile = File(...),
    job_description: str = Form(""),
    current_user: User = Depends(get_current_user),
):
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed.",
        )

    pdf_bytes = await file.read()

    resume_text, _ = extract_text_from_pdf(pdf_bytes)

    try:
        letter = generate_cover_letter(
            resume_text=resume_text,
            job_description=job_description,
        )

    except AIUnavailableError:
        # Clean 503 (with CORS headers) instead of an unhandled 500, so
        # the frontend can show a friendly "try again" message.
        raise HTTPException(
            status_code=503,
            detail=(
                "The AI service is busy right now. "
                "Please try again in a minute."
            ),
        )

    return {
        "cover_letter": letter,
    }


@router.post(
    "/resume/cover-letter/download",
    tags=["Resume"],
)
@limiter.limit(AI_RATE_LIMIT)
async def download_cover_letter(
    request: Request,
    file: UploadFile = File(...),
    job_description: str = Form(""),
    current_user: User = Depends(get_current_user),
):
    """
    Generate Cover Letter and return it as DOCX.
    """

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed.",
        )

    pdf_bytes = await file.read()

    resume_text, _ = extract_text_from_pdf(pdf_bytes)

    cover_letter = generate_cover_letter(
        resume_text=resume_text,
        job_description=job_description,
    )

    doc_buffer = generate_cover_letter_docx(
        cover_letter
    )

    return StreamingResponse(
        doc_buffer,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition":
                'attachment; filename="Cover_Letter.docx"',
        },
    )


@router.get(
    "/resume/history",
    response_model=list[ResumeHistoryItem],
    tags=["Resume"],
)
def list_resume_history(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Past resume analyses for the signed-in user, newest first. Not
    AI-backed (it's a plain DB read), so it isn't rate-limited like the
    endpoints above.
    """

    history = (
        db.query(ResumeAnalysis)
        .filter(ResumeAnalysis.user_id == current_user.id)
        .order_by(ResumeAnalysis.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return history


@router.get(
    "/resume/history/{analysis_id}",
    response_model=ResumeHistoryDetail,
    tags=["Resume"],
)
def get_resume_history_detail(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = (
        db.query(ResumeAnalysis)
        .filter(
            ResumeAnalysis.id == analysis_id,
            ResumeAnalysis.user_id == current_user.id,
        )
        .first()
    )

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Resume analysis not found.",
        )

    return record


@router.delete(
    "/resume/history/{analysis_id}",
    status_code=204,
    tags=["Resume"],
)
def delete_resume_history(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = (
        db.query(ResumeAnalysis)
        .filter(
            ResumeAnalysis.id == analysis_id,
            ResumeAnalysis.user_id == current_user.id,
        )
        .first()
    )

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Resume analysis not found.",
        )

    db.delete(record)
    db.commit()

    return Response(status_code=204)
