from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base


class AuditLog(Base):
    """
    Sprint 11: Audit & Compliance.

    Records who did what, to which entity, and (when relevant) what the
    data looked like before/after the change. Records are created
    automatically from inside routers via app.utils.audit.log_audit() -
    never through a client-facing write endpoint. Treat rows in this
    table as append-only / historical: no PUT or DELETE is exposed for
    normal application users.
    """
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Controlled vocabulary - see app.schemas.audit.AuditAction
    action = Column(String, nullable=False, index=True)

    # Controlled vocabulary - see app.schemas.audit.EntityType
    entity_type = Column(String, nullable=False, index=True)

    entity_id = Column(Integer, nullable=False, index=True)

    description = Column(Text, nullable=False)

    # Snapshot of the affected fields before/after the change.
    # Only populated for actions where a meaningful diff exists (UPDATE).
    old_value = Column(JSONB, nullable=True)
    new_value = Column(JSONB, nullable=True)

    request_method = Column(String, nullable=True)
    endpoint = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    user = relationship("User")
