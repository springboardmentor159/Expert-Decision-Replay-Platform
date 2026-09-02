from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base


class SecurityLog(Base):
    """
    Sprint 11: Security event log.

    Covers authentication and authorization events: successful/failed
    login, invalid JWT usage, unauthorized (401) and forbidden (403)
    attempts. `user_id` is nullable because a failed login may not
    resolve to a known user - in that case `identifier` holds whatever
    the client submitted (e.g. the email typed at the login form).

    NEVER write a password, JWT, or any other secret into this table.
    """
    __tablename__ = "security_logs"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    identifier = Column(String, nullable=True)

    # e.g. LOGIN_SUCCESS, LOGIN_FAILED, LOGOUT, INVALID_TOKEN,
    # UNAUTHORIZED_ACCESS, FORBIDDEN_ACCESS
    event_type = Column(String, nullable=False, index=True)

    description = Column(Text, nullable=True)
    ip_address = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    user = relationship("User")
