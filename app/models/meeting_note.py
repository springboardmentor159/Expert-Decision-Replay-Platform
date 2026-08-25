from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class MeetingNote(Base):
    __tablename__ = "meeting_notes"

    id = Column(Integer, primary_key=True, index=True)
    decision_id = Column(Integer, ForeignKey("decisions.id"), nullable=False, index=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    meeting_date = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    decision = relationship("Decision", back_populates="meeting_notes")
    creator = relationship("User", back_populates="meeting_notes")
