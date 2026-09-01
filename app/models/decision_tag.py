from sqlalchemy import Table, Column, Integer, ForeignKey

from app.db.base import Base


decision_tags = Table(
    "decision_tags",
    Base.metadata,

    Column(
        "decision_id",
        Integer,
        ForeignKey("decisions.id", ondelete="CASCADE"),
        primary_key=True
    ),

    Column(
        "tag_id",
        Integer,
        ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True
    )
)