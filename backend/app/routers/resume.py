from io import BytesIO

from fastapi import APIRouter, File, HTTPException, UploadFile
from pypdf import PdfReader

router = APIRouter()


@router.post("/resume/upload", tags=["Resume"])
async def upload_resume(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    pdf_bytes = await file.read()

    reader = PdfReader(BytesIO(pdf_bytes))

    text = ""

    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"

    return {
        "filename": file.filename,
        "pages": len(reader.pages),
        "text": text.strip()
    }