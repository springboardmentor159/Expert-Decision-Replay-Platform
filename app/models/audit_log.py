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
from app.models.enums import AuditAction, AuditEntityType


class AuditLog(Base):
    __tablename__ = "audit_log"

    __table_args__ = (
        CheckConstraint(
            "action IN ('create','update','delete','status_change','login','logout','login_failed','access','export','approve','reject')",
            name="check_valid_audit_action",
        ),
        CheckConstraint(
            "entity_type IN ('decision','alternative','comment','discussion_thread','meeting_note','user','auth','system')",
            name="check_valid_audit_entity_type",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    action = Column(
        SqlAlchemyEnum(
            AuditAction,
            name="auditaction",
            native_enum=False,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
    )
    entity_type = Column(
        SqlAlchemyEnum(
            AuditEntityType,
            name="auditentitytype",
            native_enum=False,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
    )
    entity_id = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    old_values = Column(Text, nullable=True)
    new_values = Column(Text, nullable=True)
    ip_address = Column(String, nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
