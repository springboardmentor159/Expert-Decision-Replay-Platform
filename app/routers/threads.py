from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.audit import AuditAction
from app.models.comment import Comment
from app.models.decision import Decision
from app.models.thread import DiscussionThread
from app.models.user import User, UserRole
from app.schemas.comment import (
    CommentCreate,
    CommentResponse,
)
from app.schemas.thread import (
    ThreadCreate,
    ThreadResponse,
    ThreadUpdate,
)
from app.services.audit import create_audit_log
from app.services.auth import get_current_user


router = APIRouter(
    tags=["Discussion Threads"]
)


# DECISION ACCESS HELPERS
def get_decision_or_404(
    decision_id: int,
    db: Session,
    current_user: User,
) -> Decision:
    """
    Return the decision only if it belongs to
    the current user's organization.
    """

    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if decision is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    # Organization isolation
    if decision.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    return decision


def can_access_decision(
    decision: Decision,
    current_user: User,
) -> bool:
    """
    A user can access a decision when:
    - It belongs to their organization, AND
    - They are the creator, Reviewer, Manager, or Administrator.
    """

    if decision.organization_id != current_user.organization_id:
        return False

    return (
        decision.created_by == current_user.id
        or current_user.role in (
            UserRole.REVIEWER,
            UserRole.MANAGER,
            UserRole.ADMINISTRATOR,
        )
    )



# CREATE DISCUSSION THREAD
@router.post(
    "/decisions/{decision_id}/threads",
    response_model=ThreadResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_thread(
    decision_id: int,
    thread_data: ThreadCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = get_decision_or_404(
        decision_id,
        db,
        current_user,
    )

    if not can_access_decision(
        decision,
        current_user,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You do not have permission to create "
                "a discussion thread for this decision"
            ),
        )

    thread = DiscussionThread(
        decision_id=decision.id,
        title=thread_data.title,
        created_by=current_user.id,
    )

    db.add(thread)
    db.flush()

    create_audit_log(
        db=db,
        decision_id=decision.id,
        user_id=current_user.id,
        action=AuditAction.THREAD_CREATED,
        entity_type="DiscussionThread",
        entity_id=thread.id,
        description=(
            f"Discussion thread '{thread.title}' "
            f"was created for decision '{decision.title}'"
        ),
    )

    db.commit()
    db.refresh(thread)

    return thread


# GET ALL DISCUSSION THREADS FOR A DECISION
@router.get(
    "/decisions/{decision_id}/threads",
    response_model=list[ThreadResponse],
)
def get_decision_threads(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = get_decision_or_404(
        decision_id,
        db,
        current_user,
    )

    if not can_access_decision(
        decision,
        current_user,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You do not have permission to view "
                "threads for this decision"
            ),
        )

    threads = (
        db.query(DiscussionThread)
        .filter(
            DiscussionThread.decision_id == decision_id
        )
        .order_by(DiscussionThread.created_at)
        .all()
    )

    return threads


# GET DISCUSSION THREAD BY ID
@router.get(
    "/threads/{thread_id}",
    response_model=ThreadResponse,
)
def get_thread(
    thread_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    thread = (
        db.query(DiscussionThread)
        .filter(DiscussionThread.id == thread_id)
        .first()
    )

    if thread is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion thread not found",
        )

    decision = get_decision_or_404(
        thread.decision_id,
        db,
        current_user,
    )

    if not can_access_decision(
        decision,
        current_user,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You do not have permission to view "
                "this discussion thread"
            ),
        )

    return thread


# UPDATE DISCUSSION THREAD
@router.put(
    "/threads/{thread_id}",
    response_model=ThreadResponse,
)
def update_thread(
    thread_id: int,
    thread_data: ThreadUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    thread = (
        db.query(DiscussionThread)
        .filter(DiscussionThread.id == thread_id)
        .first()
    )

    if thread is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion thread not found",
        )

    decision = get_decision_or_404(
        thread.decision_id,
        db,
        current_user,
    )

    if not can_access_decision(
        decision,
        current_user,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You do not have permission "
                "to modify this discussion thread"
            ),
        )

    # Only the thread creator can update it.
    if thread.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You can only update your own "
                "discussion threads"
            ),
        )

    thread.title = thread_data.title

    create_audit_log(
        db=db,
        decision_id=thread.decision_id,
        user_id=current_user.id,
        action=AuditAction.THREAD_UPDATED,
        entity_type="DiscussionThread",
        entity_id=thread.id,
        description=(
            f"Discussion thread '{thread.title}' "
            f"was updated"
        ),
    )

    db.commit()
    db.refresh(thread)

    return thread


# DELETE DISCUSSION THREAD
@router.delete(
    "/threads/{thread_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_thread(
    thread_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    thread = (
        db.query(DiscussionThread)
        .filter(DiscussionThread.id == thread_id)
        .first()
    )

    if thread is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion thread not found",
        )

    decision = get_decision_or_404(
        thread.decision_id,
        db,
        current_user,
    )

    if not can_access_decision(
        decision,
        current_user,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You do not have permission "
                "to delete this discussion thread"
            ),
        )

    # Only the thread creator can delete it.
    if thread.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You can only delete your own "
                "discussion threads"
            ),
        )

    decision_id = thread.decision_id
    thread_title = thread.title

    create_audit_log(
        db=db,
        decision_id=decision_id,
        user_id=current_user.id,
        action=AuditAction.DELETE,
        entity_type="DiscussionThread",
        entity_id=thread.id,
        description=(
            f"Discussion thread '{thread_title}' "
            f"was deleted"
        ),
    )

    db.delete(thread)
    db.commit()

    return None


# ADD REPLY TO DISCUSSION THREAD
@router.post(
    "/threads/{thread_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_thread_reply(
    thread_id: int,
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    thread = (
        db.query(DiscussionThread)
        .filter(DiscussionThread.id == thread_id)
        .first()
    )

    if thread is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion thread not found",
        )

    decision = get_decision_or_404(
        thread.decision_id,
        db,
        current_user,
    )

    if not can_access_decision(
        decision,
        current_user,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You do not have permission to reply "
                "to this discussion thread"
            ),
        )

    comment = Comment(
        decision_id=thread.decision_id,
        user_id=current_user.id,
        thread_id=thread.id,
        content=comment_data.content,
    )

    db.add(comment)
    db.flush()

    create_audit_log(
        db=db,
        decision_id=thread.decision_id,
        user_id=current_user.id,
        action=AuditAction.COMMENT_ADDED,
        entity_type="Comment",
        entity_id=comment.id,
        description=(
            f"Reply was added to discussion thread "
            f"'{thread.title}'"
        ),
    )

    db.commit()
    db.refresh(comment)

    return comment


# GET ALL REPLIES FOR A DISCUSSION THREAD
@router.get(
    "/threads/{thread_id}/comments",
    response_model=list[CommentResponse],
)
def get_thread_replies(
    thread_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    thread = (
        db.query(DiscussionThread)
        .filter(DiscussionThread.id == thread_id)
        .first()
    )

    if thread is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion thread not found",
        )

    decision = get_decision_or_404(
        thread.decision_id,
        db,
        current_user,
    )

    if not can_access_decision(
        decision,
        current_user,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You do not have permission to view "
                "replies in this discussion thread"
            ),
        )

    comments = (
        db.query(Comment)
        .filter(
            Comment.thread_id == thread_id
        )
        .order_by(Comment.created_at)
        .all()
    )

    return comments
