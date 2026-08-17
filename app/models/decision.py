from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Enum as SqlAlchemyEnum, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base
from app.models.enums import DecisionStatus


class Decision(Base):
    __tablename__ = "decisions"

    __table_args__ = (
        CheckConstraint(
            "status IN ('Draft', 'Under Review', 'Approved', 'Rejected', 'Archived')",
            name="check_valid_status"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    problem_statement = Column(String, nullable=False)
    category = Column(String, nullable=False)
    status = Column(
        SqlAlchemyEnum(DecisionStatus, name="decisionstatus", native_enum=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=DecisionStatus.DRAFT,
    )
    
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    creator = relationship("User", back_populates="decisions")
