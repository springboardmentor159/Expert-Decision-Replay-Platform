from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Table, Column, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


decision_tags = Table(
    "decision_tags",
    Base.metadata,
    Column("decision_id", ForeignKey("decisions.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    decisions: Mapped[list["Decision"]] = relationship(
        secondary=decision_tags, back_populates="tags"
    )