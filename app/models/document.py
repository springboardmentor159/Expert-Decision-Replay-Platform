from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql import func

from app.db.base import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    decision_id = Column(Integer, ForeignKey("decisions.id", ondelete="CASCADE"), nullable=False, index=True)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    filename = Column(String, nullable=False)
    storage_name = Column(String, unique=True, nullable=False)
    content_type = Column(String, nullable=False)
    size_bytes = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
