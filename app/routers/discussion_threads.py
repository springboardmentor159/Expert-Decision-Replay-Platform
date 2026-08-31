from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.comment import Comment
from app.models.decision import Decision
from app.models.discussion_thread import DiscussionThread
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentResponse
from app.schemas.discussion_thread import ThreadCreate, ThreadResponse, ThreadUpdate
from app.services.audit_service import get_client_ip, log_audit

router = APIRouter(tags=["Discussion Threads"])


@router.post(
    "/decisions/{decision_id}/threads",
    response_model=ThreadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a discussion thread for a decision"
)
def create_thread(
    decision_id: int,
    thread_in: ThreadCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    new_thread = DiscussionThread(
        decision_id=decision_id,
        created_by=current_user.id,
        title=thread_in.title,
        description=thread_in.description,
        status="Open"
    )
    db.add(new_thread)
    db.commit()
    db.refresh(new_thread)

    client_ip = get_client_ip(request)
    log_audit(
        db=db,
        user_id=current_user.id,
        action="CREATE",
        entity_type="DiscussionThread",
        entity_id=new_thread.id,
        description=f"User {current_user.full_name} created discussion thread '{new_thread.title}' on Decision #{decision_id}",
        new_value={"title": new_thread.title, "decision_id": decision_id, "status": new_thread.status},
        ip_address=client_ip,
        request_method=request.method,
        endpoint=str(request.url.path)
    )

    return new_thread


@router.get(
    "/decisions/{decision_id}/threads",
    response_model=List[ThreadResponse],
    status_code=status.HTTP_200_OK,
    summary="Get discussion threads for a decision"
)
def get_threads_for_decision(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    threads = db.query(DiscussionThread).filter(DiscussionThread.decision_id == decision_id).all()
    for thread in threads:
        thread.replies = db.query(Comment).filter(Comment.thread_id == thread.id).all()
    return threads


@router.get(
    "/threads/{thread_id}",
    response_model=ThreadResponse,
    status_code=status.HTTP_200_OK,
    summary="Get thread by ID"
)
def get_thread_by_id(
    thread_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    thread = db.query(DiscussionThread).filter(DiscussionThread.id == thread_id).first()
    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thread not found"
        )
    thread.replies = db.query(Comment).filter(Comment.thread_id == thread.id).all()
    return thread


@router.put(
    "/threads/{thread_id}",
    response_model=ThreadResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a discussion thread"
)
def update_thread(
    thread_id: int,
    thread_in: ThreadUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    thread = db.query(DiscussionThread).filter(DiscussionThread.id == thread_id).first()
    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thread not found"
        )

    if thread.created_by != current_user.id and current_user.role not in ["Administrator", "Manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this thread"
        )

    old_value = {
        "title": thread.title,
        "description": thread.description,
        "status": thread.status
    }

    if thread_in.title is not None:
        thread.title = thread_in.title
    if thread_in.description is not None:
        thread.description = thread_in.description
    if thread_in.status is not None:
        thread.status = thread_in.status

    db.commit()
    db.refresh(thread)

    new_value = {
        "title": thread.title,
        "description": thread.description,
        "status": thread.status
    }

    client_ip = get_client_ip(request)
    log_audit(
        db=db,
        user_id=current_user.id,
        action="UPDATE",
        entity_type="DiscussionThread",
        entity_id=thread.id,
        description=f"User {current_user.full_name} updated discussion thread '{thread.title}'",
        old_value=old_value,
        new_value=new_value,
        ip_address=client_ip,
        request_method=request.method,
        endpoint=str(request.url.path)
    )

    thread.replies = db.query(Comment).filter(Comment.thread_id == thread.id).all()
    return thread


@router.delete(
    "/threads/{thread_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a discussion thread"
)
def delete_thread(
    thread_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    thread = db.query(DiscussionThread).filter(DiscussionThread.id == thread_id).first()
    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thread not found"
        )

    if thread.created_by != current_user.id and current_user.role not in ["Administrator", "Manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this thread"
        )

    t_id = thread.id
    t_title = thread.title
    t_decision_id = thread.decision_id

    db.delete(thread)
    db.commit()

    client_ip = get_client_ip(request)
    log_audit(
        db=db,
        user_id=current_user.id,
        action="DELETE",
        entity_type="DiscussionThread",
        entity_id=t_id,
        description=f"User {current_user.full_name} deleted thread '{t_title}' from Decision #{t_decision_id}",
        ip_address=client_ip,
        request_method=request.method,
        endpoint=str(request.url.path)
    )

    return {"message": "Thread deleted successfully"}


@router.post(
    "/threads/{thread_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a reply/comment to a thread"
)
def create_thread_comment(
    thread_id: int,
    comment_in: CommentCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    thread = db.query(DiscussionThread).filter(DiscussionThread.id == thread_id).first()
    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thread not found"
        )

    new_reply = Comment(
        decision_id=thread.decision_id,
        thread_id=thread_id,
        user_id=current_user.id,
        content=comment_in.content
    )
    db.add(new_reply)
    db.commit()
    db.refresh(new_reply)

    client_ip = get_client_ip(request)
    log_audit(
        db=db,
        user_id=current_user.id,
        action="CREATE",
        entity_type="Comment",
        entity_id=new_reply.id,
        description=f"User {current_user.full_name} replied to thread '{thread.title}'",
        new_value={"content": new_reply.content, "thread_id": thread_id},
        ip_address=client_ip,
        request_method=request.method,
        endpoint=str(request.url.path)
    )

    return new_reply


@router.get(
    "/threads/{thread_id}/comments",
    response_model=List[CommentResponse],
    status_code=status.HTTP_200_OK,
    summary="Get replies/comments for a thread"
)
def get_thread_comments(
    thread_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    thread = db.query(DiscussionThread).filter(DiscussionThread.id == thread_id).first()
    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thread not found"
        )

    replies = db.query(Comment).filter(Comment.thread_id == thread_id).all()
    return replies

