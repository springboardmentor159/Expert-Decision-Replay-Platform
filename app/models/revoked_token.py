from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Index

from app.db.base import Base


class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    jti = Column(
        String(255),
        unique=True,
        nullable=False,
    )

    user_id = Column(
        Integer,
        nullable=False,
    )

    expires_at = Column(
        DateTime,
        nullable=False,
    )

    revoked_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    __table_args__ = (
        Index(
            "ix_revoked_tokens_jti",
            "jti",
        ),
        Index(
            "ix_revoked_tokens_user_id",
            "user_id",
        ),
    )