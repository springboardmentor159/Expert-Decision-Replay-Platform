from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base


class MeetingNote(Base):
    __tablename__ = "meeting_notes"

    id = Column(Integer, primary_key=True, index=True)

    decision_id = Column(Integer, ForeignKey("decisions.id"), nullable=False)

    # Taken from the authenticated JWT user, never from client input.
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    meeting_date = Column(DateTime, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    decision = relationship("Decision", back_populates="meeting_notes")
    creator = relationship("User")
