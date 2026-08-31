from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    Enum as SqlAlchemyEnum,
)
from sqlalchemy.sql import func

from app.db.base import Base
from app.models.enums import SecurityEventType


class SecurityLog(Base):
    __tablename__ = "security_log"

    __table_args__ = (
        CheckConstraint(
            "event_type IN ('login','logout','login_failed','password_changed','role_changed','token_refreshed','account_locked','unauthorized_access')",
            name="check_valid_security_event_type",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    event_type = Column(
        SqlAlchemyEnum(
            SecurityEventType,
            name="securityeventtype",
            native_enum=False,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
    )
    description = Column(Text, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
