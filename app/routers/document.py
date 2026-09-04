from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.approval import Approval
from app.models.decision import Decision
from app.models.document import DecisionDocument
from app.routers.users import get_current_user
from app.schemas.document import DocumentResponse
from app.utils.audit_logger import log_audit


router = APIRouter(tags=["Documents"])
UPLOAD_DIRECTORY = Path("uploads")
MAX_FILE_SIZE = 10 * 1024 * 1024


def _decision_or_404(decision_id: int, db: Session):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
    return decision


def _can_access(decision: Decision, user: dict, db: Session) -> bool:
    user_id = int(user["sub"])
    if user.get("role") in ("Administrator", "Manager") or decision.created_by == user_id:
        return True
    return db.query(Approval).filter(
        Approval.decision_id == decision.id,
        Approval.reviewer_id == user_id,
    ).first() is not None


def _response(document: DecisionDocument) -> DocumentResponse:
    return DocumentResponse(
        id=document.id,
        decision_id=document.decision_id,
        uploaded_by=document.uploaded_by,
        original_filename=document.original_filename,
        content_type=document.content_type,
        file_size=document.file_size,
        created_at=document.created_at,
        download_url=f"/documents/{document.id}/download",
    )


@router.post("/decisions/{decision_id}/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    decision_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    decision = _decision_or_404(decision_id, db)
    if not _can_access(decision, current_user, db):
        raise HTTPException(status_code=403, detail="You cannot upload documents for this decision")
    if not file.filename:
        raise HTTPException(status_code=422, detail="A file name is required")

    contents = await file.read(MAX_FILE_SIZE + 1)
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File exceeds the 10 MB limit")

    UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)
    stored_filename = f"{uuid4().hex}.bin"
    (UPLOAD_DIRECTORY / stored_filename).write_bytes(contents)
    document = DecisionDocument(
        decision_id=decision_id,
        uploaded_by=int(current_user["sub"]),
        original_filename=Path(file.filename).name,
        stored_filename=stored_filename,
        content_type=file.content_type or "application/octet-stream",
        file_size=len(contents),
    )
    db.add(document)
    db.flush()
    log_audit(db, int(current_user["sub"]), "CREATE", "Document", document.id, f"Document {document.id} uploaded", new_value={"decision_id": decision_id, "file_size": len(contents)})
    try:
        db.commit()
    except Exception:
        db.rollback()
        (UPLOAD_DIRECTORY / stored_filename).unlink(missing_ok=True)
        raise
    db.refresh(document)
    return _response(document)


@router.get("/decisions/{decision_id}/documents", response_model=list[DocumentResponse])
def list_documents(decision_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    decision = _decision_or_404(decision_id, db)
    if not _can_access(decision, current_user, db):
        raise HTTPException(status_code=403, detail="You cannot access documents for this decision")
    return [_response(document) for document in db.query(DecisionDocument).filter(DecisionDocument.decision_id == decision_id).order_by(DecisionDocument.created_at.desc()).all()]


@router.get("/documents/{document_id}/download")
def download_document(document_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    document = db.query(DecisionDocument).filter(DecisionDocument.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    decision = _decision_or_404(document.decision_id, db)
    if not _can_access(decision, current_user, db):
        raise HTTPException(status_code=403, detail="You cannot access this document")
    path = UPLOAD_DIRECTORY / document.stored_filename
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Stored file not found")
    return FileResponse(path, media_type=document.content_type, filename=document.original_filename)
