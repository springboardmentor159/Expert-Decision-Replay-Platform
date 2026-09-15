from pathlib import Path
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.auth import get_current_user
from app.models.attachment import DecisionAttachment
from app.models.decision import Decision
from app.models.user import User, UserRole
from app.schemas.attachment import AttachmentResponse
from app.services.storage import delete_stored_file, save_upload_file

router = APIRouter(tags=["Attachments & Documents"])


@router.post("/decisions/{decision_id}/attachments", response_model=AttachmentResponse, status_code=status.HTTP_201_CREATED)
def upload_decision_attachment(
    decision_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Decision not found.")

    if current_user.role not in (UserRole.ADMINISTRATOR, UserRole.MANAGER) and decision.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to attach documents to this decision.",
        )

    file_path, original_filename, file_size = save_upload_file(file, decision_id)

    attachment = DecisionAttachment(
        decision_id=decision_id,
        filename=original_filename,
        file_path=file_path,
        file_size=file_size,
        content_type=file.content_type,
        uploaded_by=current_user.id,
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    return attachment


@router.get("/decisions/{decision_id}/attachments", response_model=list[AttachmentResponse])
def list_decision_attachments(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Decision not found.")

    return db.query(DecisionAttachment).filter(DecisionAttachment.decision_id == decision_id).all()


@router.get("/attachments/archive", response_model=list[AttachmentResponse])
def list_all_attachments_archive(
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = (
        db.query(DecisionAttachment)
        .join(Decision, DecisionAttachment.decision_id == Decision.id)
    )
    if current_user.organization_id:
        query = query.filter(Decision.organization_id == current_user.organization_id)
    return query.order_by(DecisionAttachment.created_at.desc()).limit(limit).all()


@router.get("/attachments/{attachment_id}/download")
def download_attachment(
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    attachment = db.query(DecisionAttachment).filter(DecisionAttachment.id == attachment_id).first()
    if not attachment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found.")

    file_path = Path(attachment.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File content not found on disk.")

    return FileResponse(
        path=str(file_path),
        filename=attachment.filename,
        media_type=attachment.content_type or "application/octet-stream",
    )


@router.delete("/attachments/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_attachment(
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    attachment = db.query(DecisionAttachment).filter(DecisionAttachment.id == attachment_id).first()
    if not attachment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found.")

    decision = db.query(Decision).filter(Decision.id == attachment.decision_id).first()
    if (
        current_user.role not in (UserRole.ADMINISTRATOR, UserRole.MANAGER)
        and attachment.uploaded_by != current_user.id
        and (decision and decision.created_by != current_user.id)
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this attachment.",
        )

    delete_stored_file(attachment.file_path)
    db.delete(attachment)
    db.commit()
    return None
