from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base


class DecisionVersion(Base):
    __tablename__ = "decision_versions"

    id = Column(Integer, primary_key=True, index=True)

    decision_id = Column(
        Integer,
        ForeignKey("decisions.id"),
        nullable=False,
        index=True
    )

    version_number = Column(Integer, nullable=False)

    title = Column(Text, nullable=False)

    description = Column(Text, nullable=True)

    status = Column(Text, nullable=False)

    created_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    decision = relationship(
        "Decision",
        back_populates="versions"
    )

    user = relationship(
        "User",
        back_populates="decision_versions"
    )