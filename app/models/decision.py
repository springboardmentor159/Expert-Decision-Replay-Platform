from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from app.core.enums import DecisionStatus
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.db.base import Base


class Decision(Base):
    __tablename__ = "decisions"

    alternatives = relationship(
    "Alternative",
    back_populates="decision",
    cascade="all, delete-orphan"
)

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, nullable=False)

    problem_statement = Column(Text, nullable=False)
    rationale = Column(
    Text,
    nullable=True
)

    category = Column(String, nullable=False)

    status = Column(
    Enum(
        DecisionStatus,
        name="decision_status",
        values_callable=lambda enum: [item.value for item in enum]
    ),
    nullable=False,
    default=DecisionStatus.DRAFT
)

    created_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = Column(
    DateTime(timezone=True),
    server_default=func.now(),
    onupdate=func.now(),
    nullable=False
)

    creator = relationship(
        "User",
        back_populates="decisions"
    )
    comments = relationship(
    "Comment",
    back_populates="decision"
)
    meeting_notes = relationship(
    "MeetingNote",
    back_populates="decision"
)