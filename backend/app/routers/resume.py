from fastapi import APIRouter, UploadFile, File, HTTPException

router = APIRouter()


@router.post("/resume/upload", tags=["Resume"])
async def upload_resume(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "message": "Resume uploaded successfully."
    }