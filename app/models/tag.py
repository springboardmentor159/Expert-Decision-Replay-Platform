from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    UniqueConstraint
)
from sqlalchemy.orm import relationship

from app.db.base import Base


# ============================================================
# Decision ↔ Tag association table
# ============================================================

decision_tags = Table(
    "decision_tags",
    Base.metadata,

    Column(
        "decision_id",
        Integer,
        ForeignKey("decisions.id"),
        primary_key=True
    ),

    Column(
        "tag_id",
        Integer,
        ForeignKey("tags.id"),
        primary_key=True
    )
)


# ============================================================
# Tag Model
# ============================================================

class Tag(Base):

    __tablename__ = "tags"

    # --------------------------------------------------------
    # Primary Key
    # --------------------------------------------------------

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # --------------------------------------------------------
    # Organization
    # --------------------------------------------------------

    organization_id = Column(
        Integer,
        ForeignKey("organizations.id"),
        nullable=False,
        index=True
    )

    # --------------------------------------------------------
    # Tag name
    # --------------------------------------------------------

    name = Column(
        String,
        nullable=False
    )

    # --------------------------------------------------------
    # Created timestamp
    # --------------------------------------------------------

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # --------------------------------------------------------
    # Organization relationship
    # --------------------------------------------------------

    organization = relationship(
        "Organization",
        back_populates="tags"
    )

    # --------------------------------------------------------
    # Decision relationship
    # --------------------------------------------------------

    decisions = relationship(
        "Decision",
        secondary=decision_tags,
        back_populates="tags"
    )

    # --------------------------------------------------------
    # A tag name must be unique only inside an organization.
    #
    # Organization A:
    #     Urgent
    #
    # Organization B:
    #     Urgent
    #
    # Both are allowed.
    # --------------------------------------------------------

    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "name",
            name="uq_tag_organization_name"
        ),
    )