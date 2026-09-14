import os
import uuid
from typing import List

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.decision import Decision
from app.models.attachment import Attachment
from app.schemas.attachment import AttachmentResponse
from app.services.activity import create_activity
from app.services.audit import create_audit_log


router = APIRouter(
    tags=["Attachments"],
)


UPLOAD_DIR = "uploads/attachments"

os.makedirs(UPLOAD_DIR, exist_ok=True)


ALLOWED_EXTENSIONS = {
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",
    ".txt",
    ".png",
    ".jpg",
    ".jpeg",
}


MAX_FILE_SIZE = 10 * 1024 * 1024


@router.post(
    "/decisions/{decision_id}/attachments",
    response_model=AttachmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_attachment(
    decision_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    original_filename = file.filename or "unknown"

    extension = os.path.splitext(
        original_filename
    )[1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "File type not allowed. "
                "Allowed files: PDF, DOC, DOCX, XLS, XLSX, "
                "PPT, PPTX, TXT, PNG, JPG, JPEG."
            ),
        )

    file_content = await file.read()

    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size must not exceed 10 MB.",
        )

    stored_filename = (
        f"{uuid.uuid4().hex}{extension}"
    )

    file_path = os.path.join(
        UPLOAD_DIR,
        stored_filename,
    )

    with open(file_path, "wb") as buffer:
        buffer.write(file_content)

    attachment = Attachment(
        decision_id=decision_id,
        uploaded_by=current_user.id,
        original_filename=original_filename,
        stored_filename=stored_filename,
        file_path=file_path,
        content_type=file.content_type,
        file_size=len(file_content),
    )

    db.add(attachment)
    db.flush()

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="CREATE",
        entity_type="Attachment",
        entity_id=attachment.id,
        description=(
            f"User {current_user.id} uploaded "
            f"Attachment {attachment.id}"
        ),
        new_value={
            "decision_id": decision_id,
            "uploaded_by": current_user.id,
            "original_filename": original_filename,
            "file_size": len(file_content),
        },
        request_method="POST",
        endpoint=(
            f"/decisions/{decision_id}/attachments"
        ),
    )

    create_activity(
        db=db,
        user_id=current_user.id,
        action="Attachment uploaded",
        entity_type="Attachment",
        entity_id=attachment.id,
        description=(
            f"User {current_user.id} uploaded "
            f"{original_filename}"
        ),
    )

    db.commit()
    db.refresh(attachment)

    return attachment


@router.get(
    "/decisions/{decision_id}/attachments",
    response_model=List[AttachmentResponse],
)
def get_attachments(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    return (
        db.query(Attachment)
        .filter(
            Attachment.decision_id == decision_id
        )
        .order_by(Attachment.created_at.asc())
        .all()
    )
@router.delete("/attachments/{attachment_id}")
def delete_attachment(
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    attachment = (
        db.query(Attachment)
        .filter(Attachment.id == attachment_id)
        .first()
    )

    if not attachment:
        raise HTTPException(
            status_code=404,
            detail="Attachment not found"
        )

    if attachment.uploaded_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own attachments"
        )

    file_path = attachment.file_path

    db.delete(attachment)
    db.commit()

    if file_path and os.path.exists(file_path):
        os.remove(file_path)

    return {
        "message": "Attachment deleted successfully"
    }