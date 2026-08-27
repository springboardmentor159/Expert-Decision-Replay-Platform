from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    Text,
    DateTime,
    ForeignKey
)
from sqlalchemy.orm import relationship

from app.base import Base


class Comment(Base):
    __tablename__ = "comments"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    decision_id = Column(
        Integer,
        ForeignKey(
            "decisions.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    user_id = Column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    content = Column(
        Text,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    decision = relationship(
        "Decision",
        back_populates="comments"
    )

    user = relationship(
        "User"
    )