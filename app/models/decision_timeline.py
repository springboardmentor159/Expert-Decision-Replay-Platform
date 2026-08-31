from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    DateTime,
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class DecisionTimeline(Base):
    __tablename__ = "decision_timeline"

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

    event_type = Column(
        String,
        nullable=False
    )

    description = Column(
        Text,
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # ==========================================
    # RELATIONSHIP
    # ==========================================
    decision = relationship(
        "Decision",
        back_populates="timeline_events"
    )