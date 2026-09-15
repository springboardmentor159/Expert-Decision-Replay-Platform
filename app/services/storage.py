import os
import shutil
import uuid
from pathlib import Path
from fastapi import UploadFile

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def save_upload_file(file: UploadFile, decision_id: int) -> tuple[str, str, int]:
    """
    Saves an uploaded file to local disk under uploads/{decision_id}/.
    Returns: (stored_file_path, sanitized_filename, file_size_bytes)
    """
    decision_dir = UPLOAD_DIR / str(decision_id)
    decision_dir.mkdir(parents=True, exist_ok=True)

    original_name = file.filename or "attachment"
    sanitized_name = os.path.basename(original_name).replace(" ", "_")
    unique_prefix = uuid.uuid4().hex[:8]
    stored_name = f"{unique_prefix}_{sanitized_name}"
    target_path = decision_dir / stored_name

    with target_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = target_path.stat().st_size
    return str(target_path), original_name, file_size


def delete_stored_file(file_path: str) -> None:
    path = Path(file_path)
    if path.exists() and path.is_file():
        try:
            path.unlink()
        except OSError:
            pass
