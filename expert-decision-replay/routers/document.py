import os
import uuid
from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.document import Document
from app.models.decision import Decision
from app.schemas.document import DocumentResponse


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


UPLOAD_DIR = Path("uploads/documents")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


ALLOWED_EXTENSIONS = {
    ".pdf",
    ".doc",
    ".docx",
    ".txt",
    ".png",
    ".jpg",
    ".jpeg",
}


MAX_FILE_SIZE = 10 * 1024 * 1024


@router.post(
    "/decisions/{decision_id}/upload",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    decision_id: int,
    file: UploadFile = File(...),
    document_type: str | None = Form(default=None),
    description: str | None = Form(default=None),
    db: Session = Depends(get_db),
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

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File name is required",
        )

    original_name = Path(file.filename).name
    file_extension = Path(original_name).suffix.lower()

    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Unsupported file type. Allowed types: "
                "PDF, DOC, DOCX, TXT, PNG, JPG, JPEG"
            ),
        )

    file_content = await file.read()

    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size must not exceed 10 MB",
        )

    stored_file_name = (
        f"{uuid.uuid4().hex}{file_extension}"
    )

    stored_file_path = UPLOAD_DIR / stored_file_name
    stored_file_path.write_bytes(file_content)

    document = Document(
        decision_id=decision_id,
        uploaded_by=decision.created_by,
        file_name=original_name,
        file_path=str(stored_file_path),
        document_type=document_type,
        description=description,
    )

    try:
        db.add(document)
        db.commit()
        db.refresh(document)
    except Exception:
        db.rollback()

        if stored_file_path.exists():
            stored_file_path.unlink()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Document could not be saved",
        )

    return document


@router.get(
    "/decisions/{decision_id}",
    response_model=list[DocumentResponse],
)
def get_documents(
    decision_id: int,
    db: Session = Depends(get_db),
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
        db.query(Document)
        .filter(Document.decision_id == decision_id)
        .order_by(Document.uploaded_at.desc())
        .all()
    )


@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    stored_file_path = Path(document.file_path)

    db.delete(document)
    db.commit()

    if stored_file_path.exists():
        stored_file_path.unlink()

    return {
        "message": "Document deleted successfully",
        "document_id": document_id,
    }