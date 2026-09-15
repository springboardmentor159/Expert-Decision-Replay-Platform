from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.auth import get_current_user
from app.models.alternative import Alternative
from app.models.approval import Approval
from app.models.attachment import DecisionAttachment
from app.models.audit import AuditLog, DecisionVersion
from app.models.comment import Comment
from app.models.decision import Decision
from app.models.meeting_note import MeetingNote
from app.models.thread import DiscussionThread
from app.models.user import User

router = APIRouter(prefix="/decisions", tags=["Decision Replay"])


class ReplayMilestone(BaseModel):
    id: str
    timestamp: datetime
    event_type: str  # CREATION, ALTERNATIVE, APPROVAL, COMMENT, THREAD, MEETING_NOTE, VERSION, ATTACHMENT, STATUS_CHANGE
    title: str
    description: str
    actor_name: str | None = None
    actor_role: str | None = None
    badge_color: str = "primary"
    metadata: dict = {}


class DecisionReplayResponse(BaseModel):
    decision_id: int
    title: str
    current_status: str
    implementation_status: str
    final_outcomes: str | None = None
    evaluation_criteria: str | None = None
    total_milestones: int
    milestones: list[ReplayMilestone]


@router.get("/{decision_id}/replay", response_model=DecisionReplayResponse)
def get_decision_replay(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Decision not found.")

    milestones: list[ReplayMilestone] = []

    # 1. Decision Creation
    creator_name = decision.user.full_name if decision.user else "Unknown"
    creator_role = decision.user.role.value if decision.user else "Employee"
    milestones.append(
        ReplayMilestone(
            id=f"create-{decision.id}",
            timestamp=decision.created_at,
            event_type="CREATION",
            title="Decision Proposed",
            description=f"Initial draft created by {creator_name} under category '{decision.category}'.",
            actor_name=creator_name,
            actor_role=creator_role,
            badge_color="info",
            metadata={"problem_statement": decision.problem_statement[:150]},
        )
    )

    # 2. Alternatives
    alternatives = db.query(Alternative).filter(Alternative.decision_id == decision_id).all()
    for alt in alternatives:
        milestones.append(
            ReplayMilestone(
                id=f"alt-{alt.id}",
                timestamp=alt.created_at,
                event_type="ALTERNATIVE",
                title=f"Alternative Added: {alt.name}",
                description=f"Option evaluated with Cost: ${alt.estimated_cost}, Risk: {alt.risk_level.value}, Feasibility: {alt.feasibility_score}/5.",
                badge_color="warning",
                metadata={"feasibility": alt.feasibility_score, "cost": float(alt.estimated_cost)},
            )
        )

    # 3. Approvals & Reviews
    approvals = db.query(Approval).filter(Approval.decision_id == decision_id).all()
    for apprv in approvals:
        rev_name = apprv.reviewer.full_name if apprv.reviewer else "Reviewer"
        rev_role = apprv.reviewer.role.value if apprv.reviewer else "Reviewer"
        milestones.append(
            ReplayMilestone(
                id=f"apprv-req-{apprv.id}",
                timestamp=apprv.created_at,
                event_type="APPROVAL_ASSIGNMENT",
                title=f"Reviewer Assigned: {rev_name}",
                description=f"Review request sent (Level {apprv.sequence_order}).",
                actor_name=rev_name,
                actor_role=rev_role,
                badge_color="primary",
            )
        )
        if apprv.completed_at:
            is_approved = apprv.status.value == "Approved"
            milestones.append(
                ReplayMilestone(
                    id=f"apprv-res-{apprv.id}",
                    timestamp=apprv.completed_at,
                    event_type="APPROVAL_COMPLETION",
                    title=f"Review {apprv.status.value} by {rev_name}",
                    description=f"{rev_name} completed evaluation with decision: {apprv.status.value}.",
                    actor_name=rev_name,
                    actor_role=rev_role,
                    badge_color="success" if is_approved else "danger",
                )
            )

    # 4. Attachments
    attachments = db.query(DecisionAttachment).filter(DecisionAttachment.decision_id == decision_id).all()
    for att in attachments:
        up_name = att.uploader.full_name if att.uploader else "User"
        milestones.append(
            ReplayMilestone(
                id=f"att-{att.id}",
                timestamp=att.created_at,
                event_type="ATTACHMENT",
                title=f"Document Uploaded: {att.filename}",
                description=f"{att.filename} ({att.file_size} bytes) attached by {up_name}.",
                actor_name=up_name,
                badge_color="info",
            )
        )

    # 5. Meeting Notes
    notes = db.query(MeetingNote).filter(MeetingNote.decision_id == decision_id).all()
    for note in notes:
        n_user = note.user.full_name if note.user else "User"
        milestones.append(
            ReplayMilestone(
                id=f"note-{note.id}",
                timestamp=note.created_at,
                event_type="MEETING_NOTE",
                title=f"Meeting Note: {note.title}",
                description=note.notes[:160] + ("..." if len(note.notes) > 160 else ""),
                actor_name=n_user,
                badge_color="accent",
            )
        )

    # 6. Audit Logs (Status changes & versions)
    status_logs = (
        db.query(AuditLog)
        .filter(AuditLog.decision_id == decision_id, AuditLog.action == "STATUS_CHANGE")
        .all()
    )
    for log in status_logs:
        milestones.append(
            ReplayMilestone(
                id=f"status-{log.id}",
                timestamp=log.created_at,
                event_type="STATUS_CHANGE",
                title=f"Status Changed: {log.new_value}",
                description=log.description,
                badge_color="purple",
            )
        )

    # Sort all milestones chronologically
    milestones.sort(key=lambda m: m.timestamp)

    return DecisionReplayResponse(
        decision_id=decision.id,
        title=decision.title,
        current_status=decision.status.value,
        implementation_status=decision.implementation_status.value,
        final_outcomes=decision.final_outcomes,
        evaluation_criteria=decision.evaluation_criteria,
        total_milestones=len(milestones),
        milestones=milestones,
    )
