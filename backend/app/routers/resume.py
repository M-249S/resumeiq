from io import BytesIO

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from pypdf import PdfReader

from app.schemas.resume import ResumeUploadResponse
from app.schemas.cover_letter import CoverLetterResponse

from app.services.ai_service import analyze_resume
from app.services.cover_letter_service import generate_cover_letter
from app.services.gemini_service import rewrite_resume
from app.services.pdf_service import generate_resume_pdf

router = APIRouter()


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
async def upload_resume(
    file: UploadFile = File(...),
    job_description: str = Form(""),
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

    return {
        "filename": file.filename,
        "pages": pages,
        "analysis": analysis,
    }


@router.post(
    "/resume/improve",
    tags=["Resume"],
)
async def improve_resume(
    file: UploadFile = File(...),
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
async def download_resume(
    file: UploadFile = File(...),
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
async def cover_letter(
    file: UploadFile = File(...),
    job_description: str = Form(...),
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