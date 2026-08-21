from datetime import datetime

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class MeetingNote(Base):
    __tablename__ = "meeting_notes"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    decision_id = Column(
        Integer,
        ForeignKey("decisions.id"),
        nullable=False
    )

    created_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    title = Column(
        String,
        nullable=False
    )

    content = Column(
        Text,
        nullable=False
    )

    meeting_date = Column(
        Date,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    decision = relationship(
        "Decision",
        back_populates="meeting_notes"
    )

    user = relationship(
        "User",
        back_populates="meeting_notes"
    )