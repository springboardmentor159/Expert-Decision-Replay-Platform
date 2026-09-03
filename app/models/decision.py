from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Decision(Base):
    __tablename__ = "decisions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    problem_statement: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="Draft")
    rationale: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user: Mapped["User"] = relationship(back_populates="decisions")
    alternatives: Mapped[list["Alternative"]] = relationship(back_populates="decision", cascade="all, delete-orphan")
    comments: Mapped[list["Comment"]] = relationship(back_populates="decision", cascade="all, delete-orphan")
    discussion_threads: Mapped[list["DiscussionThread"]] = relationship(back_populates="decision", cascade="all, delete-orphan")
    meeting_notes: Mapped[list["MeetingNote"]] = relationship(back_populates="decision", cascade="all, delete-orphan")
    tags: Mapped[list["Tag"]] = relationship(secondary="decision_tags", back_populates="decisions")
