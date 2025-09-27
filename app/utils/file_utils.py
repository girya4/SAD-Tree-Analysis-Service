import os
import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException, status
from config import settings


def validate_file(file: UploadFile) -> None:
    """Validate uploaded file"""
    # Check file size
    if file.size and file.size > settings.max_file_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size is {settings.max_file_size} bytes"
        )
    
    # Check file extension
    if file.filename:
        file_extension = Path(file.filename).suffix.lower().lstrip('.')
        allowed_extensions = settings.allowed_extensions.split(',')
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
            )


def generate_unique_filename(original_filename: str) -> str:
    """Generate unique filename for uploaded file"""
    file_extension = Path(original_filename).suffix
    unique_id = str(uuid.uuid4())
    return f"{unique_id}{file_extension}"


def save_uploaded_file(file: UploadFile, filename: str) -> str:
    """Save uploaded file to disk and return the path"""
    # Create upload directory if it doesn't exist
    upload_dir = Path(settings.upload_dir)
    original_dir = upload_dir / "original"
    original_dir.mkdir(parents=True, exist_ok=True)
    
    # Save file
    file_path = original_dir / filename
    with open(file_path, "wb") as buffer:
        content = file.file.read()
        buffer.write(content)
    
    return str(file_path)


def create_processed_dir() -> Path:
    """Create processed directory if it doesn't exist"""
    upload_dir = Path(settings.upload_dir)
    processed_dir = upload_dir / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    return processed_dir


def get_file_size(file_path: str) -> int:
    """Get file size in bytes"""
    return os.path.getsize(file_path)
