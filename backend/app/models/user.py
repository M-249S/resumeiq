from typing import TYPE_CHECKING

from sqlalchemy import String

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.models.base import Base

if TYPE_CHECKING:
    # Only imported for type-checkers/linters — importing this for real at
    # module load time would create a circular import with
    # app.resume.models (which imports User the same way, in reverse).
    from app.resume.models import ResumeAnalysis


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    full_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        default=True,
    )

    resume_analyses: Mapped[list["ResumeAnalysis"]] = relationship(
        "ResumeAnalysis",
        back_populates="user",
        cascade="all, delete-orphan",
    )
