from io import BytesIO
from sqlalchemy.orm import Session

from fastapi import Depends
from fastapi import Request

from app.core.limiter import limiter

from app.db.session import get_db
from app.auth.dependencies import get_current_user

from app.models.user import User
from app.resume.models import ResumeAnalysis
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from pypdf import PdfReader

from app.schemas.resume import ResumeUploadResponse
from app.schemas.cover_letter import CoverLetterResponse

from app.services.ai_service import analyze_resume
from app.services.cover_letter_service import generate_cover_letter
from app.services.gemini_service import rewrite_resume
from app.services.pdf_service import generate_resume_pdf
from app.services.word_service import generate_cover_letter_docx
router = APIRouter()

# Per-IP limit for the AI-backed endpoints below. Each of these calls a
# paid AI provider, so they're limited to avoid runaway costs from a
# single client hammering the API.
AI_RATE_LIMIT = "5/minute"


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

    letter = generate_cover_letter(
        resume_text=resume_text,
        job_description=job_description,
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
