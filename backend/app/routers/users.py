from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from pydantic import BaseModel

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.session import get_db

from app.auth.dependencies import get_current_user

from app.models.user import User
from app.resume.models import ResumeAnalysis

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


class DeleteAccountRequest(BaseModel):
    # Typed by the user to confirm. Works for password and Google accounts
    # alike (Google-created accounts have no password to re-enter).
    confirm_email: str


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_account(
    payload: DeleteAccountRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Permanently delete the signed-in user and all of their analyses.

    The caller must type their own email address as confirmation, so a
    stray request (or a stolen-but-unattended session click) cannot wipe
    an account by accident.
    """
    if payload.confirm_email.strip().lower() != current_user.email.lower():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The email you typed does not match your account.",
        )

    user = db.get(User, current_user.id)

    if user is not None:
        # resume_analyses are removed by the ORM cascade on the relationship.
        db.delete(user)
        db.commit()

    return None


def _get_owned_analysis(
    analysis_id: int,
    db: Session,
    current_user: User,
) -> ResumeAnalysis:
    analysis = (
        db.query(ResumeAnalysis)
        .filter(
            ResumeAnalysis.id == analysis_id,
            ResumeAnalysis.user_id == current_user.id,
        )
        .first()
    )

    if analysis is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found.",
        )

    return analysis


@router.get("/me/analyses")
def get_my_analyses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    analyses = (
        db.query(ResumeAnalysis)
        .filter(
            ResumeAnalysis.user_id == current_user.id
        )
        .order_by(
            ResumeAnalysis.created_at.desc()
        )
        .all()
    )

    return analyses


@router.get("/me/analyses/{analysis_id}")
def get_my_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _get_owned_analysis(analysis_id, db, current_user)


@router.delete("/me/analyses/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    analysis = _get_owned_analysis(analysis_id, db, current_user)

    db.delete(analysis)
    db.commit()

    return None


@router.get("/me/dashboard")
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    analyses = (
        db.query(ResumeAnalysis)
        .filter(
            ResumeAnalysis.user_id == current_user.id
        )
        .order_by(
            ResumeAnalysis.created_at.desc()
        )
        .all()
    )

    total_analyses = len(analyses)

    average_score = (
        db.query(func.avg(ResumeAnalysis.score))
        .filter(
            ResumeAnalysis.user_id == current_user.id
        )
        .scalar()
    ) or 0

    average_match_score = (
        db.query(func.avg(ResumeAnalysis.match_score))
        .filter(
            ResumeAnalysis.user_id == current_user.id
        )
        .scalar()
    ) or 0

    best_score = (
        db.query(func.max(ResumeAnalysis.score))
        .filter(
            ResumeAnalysis.user_id == current_user.id
        )
        .scalar()
    ) or 0

    recent = [
        {
            "id": item.id,
            "filename": item.filename,
            "score": item.score,
            "match_score": item.match_score,
            "created_at": item.created_at,
        }
        for item in analyses[:5]
    ]

    return {
        "total_analyses": total_analyses,
        "average_score": round(float(average_score), 1),
        "average_match_score": round(float(average_match_score), 1),
        "best_score": best_score,
        "recent": recent,
    }
