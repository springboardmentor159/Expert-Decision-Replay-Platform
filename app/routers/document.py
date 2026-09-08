import re
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.models.decision import Decision
from app.models.document import Document
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.document import DocumentResponse
from app.services.audit import log_audit

router = APIRouter(prefix="/decisions", tags=["Documents"])

UPLOAD_ROOT = Path("uploads") / "documents"
MAX_FILE_SIZE = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".csv", ".png", ".jpg", ".jpeg"}


def _decision_or_404(db: Session, decision_id: int) -> Decision:
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
    return decision


def _document_or_404(db: Session, document_id: int) -> Document:
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


def _can_modify(decision: Decision, current_user: User) -> bool:
    return decision.created_by == current_user.id or current_user.role == UserRole.ADMINISTRATOR


def _response(document: Document) -> DocumentResponse:
    return DocumentResponse(
        id=document.id,
        decision_id=document.decision_id,
        uploaded_by=document.uploaded_by,
        filename=document.filename,
        content_type=document.content_type,
        size_bytes=document.size_bytes,
        created_at=document.created_at,
        download_url=f"/decisions/documents/{document.id}/download",
    )


@router.get("/{decision_id}/documents", response_model=list[DocumentResponse])
def list_documents(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _decision_or_404(db, decision_id)
    documents = db.query(Document).filter(Document.decision_id == decision_id).order_by(Document.created_at.desc()).all()
    return [_response(document) for document in documents]


@router.post("/{decision_id}/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    request: Request,
    decision_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = _decision_or_404(db, decision_id)
    if not _can_modify(decision, current_user):
        raise HTTPException(status_code=403, detail="Not authorized to upload documents for this decision")

    original_name = Path(file.filename or "").name
    extension = Path(original_name).suffix.lower()
    if not original_name or not re.fullmatch(r"[^\\/]+", original_name) or extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=422, detail="Invalid file type. Upload a supported document or image file.")

    content = await file.read(MAX_FILE_SIZE + 1)
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File is too large. Maximum size is 10 MB.")

    storage_name = f"{uuid4().hex}{extension}"
    UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
    (UPLOAD_ROOT / storage_name).write_bytes(content)
    document = Document(
        decision_id=decision_id,
        uploaded_by=current_user.id,
        filename=original_name,
        storage_name=storage_name,
        content_type=file.content_type or "application/octet-stream",
        size_bytes=len(content),
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    log_audit(db, current_user.id, "create", "document", document.id, f"Uploaded document '{original_name}' for decision {decision_id}", ip_address=request.client.host if request.client else None)
    return _response(document)


@router.get("/documents/{document_id}/download")
def download_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = _document_or_404(db, document_id)
    path = UPLOAD_ROOT / document.storage_name
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Document file is unavailable")
    return FileResponse(path, media_type=document.content_type, filename=document.filename)


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    request: Request,
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = _document_or_404(db, document_id)
    decision = _decision_or_404(db, document.decision_id)
    if document.uploaded_by != current_user.id and not _can_modify(decision, current_user):
        raise HTTPException(status_code=403, detail="Not authorized to delete this document")
    path = UPLOAD_ROOT / document.storage_name
    if path.is_file():
        path.unlink()
    db.delete(document)
    db.commit()
    log_audit(db, current_user.id, "delete", "document", document_id, f"Deleted document '{document.filename}'", ip_address=request.client.host if request.client else None)
    return None
