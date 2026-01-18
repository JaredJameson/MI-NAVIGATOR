"""
File Upload API Endpoints
"""

import os
import uuid
from datetime import datetime
from typing import List, Optional
import mimetypes

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.uploaded_file import UploadedFile

router = APIRouter()

# File upload configuration
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "../../../uploads")
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
ALLOWED_MIME_TYPES = [
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # DOCX
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # XLSX
    "text/csv",
    "image/png",
    "image/jpeg",
]
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".xlsx", ".csv", ".png", ".jpg", ".jpeg"}


class FileUploadResponse(BaseModel):
    id: str
    original_name: str
    file_type: str
    file_size: int
    created_at: datetime
    extracted_content: Optional[str] = None


def get_file_extension(filename: str) -> str:
    """Extract file extension from filename."""
    return os.path.splitext(filename)[1].lower()


def validate_file(file: UploadFile) -> None:
    """Validate uploaded file."""
    # Check file extension
    ext = get_file_extension(file.filename)
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Check MIME type if available
    if file.content_type and file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {file.content_type}"
        )


async def extract_text_content(file_path: str, file_type: str) -> Optional[str]:
    """Extract text content from uploaded file."""
    try:
        if file_type == "application/pdf":
            # PDF extraction (requires PyPDF2 or pypdf)
            try:
                import PyPDF2
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
                    return text.strip()
            except ImportError:
                return "[PDF text extraction not available - PyPDF2 not installed]"
            except Exception as e:
                return f"[PDF extraction error: {str(e)}]"

        elif "wordprocessingml" in file_type:  # DOCX
            # DOCX extraction (requires python-docx)
            try:
                from docx import Document
                doc = Document(file_path)
                text = "\n".join([para.text for para in doc.paragraphs])
                return text.strip()
            except ImportError:
                return "[DOCX text extraction not available - python-docx not installed]"
            except Exception as e:
                return f"[DOCX extraction error: {str(e)}]"

        elif file_type == "text/csv":
            # CSV - just read as text
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()

        else:
            # For images and other types, no text extraction
            return None

    except Exception as e:
        return f"[Text extraction error: {str(e)}]"


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    conversation_id: Optional[str] = None,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a file for use in chat/analysis.

    - **file**: File to upload (PDF, DOCX, XLSX, CSV, PNG, JPG - max 50MB)
    - **conversation_id**: Optional conversation ID to link file to
    """
    # Validate file
    validate_file(file)

    # Read file content
    content = await file.read()
    file_size = len(content)

    # Check file size
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024} MB"
        )

    # Generate unique filename
    file_id = str(uuid.uuid4())
    ext = get_file_extension(file.filename)
    stored_filename = f"{file_id}{ext}"
    file_path = os.path.join(UPLOAD_DIR, stored_filename)

    # Ensure upload directory exists
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # Save file to disk
    with open(file_path, "wb") as f:
        f.write(content)

    # Detect MIME type
    mime_type = file.content_type or mimetypes.guess_type(file.filename)[0] or "application/octet-stream"

    # Extract text content
    extracted_content = await extract_text_content(file_path, mime_type)

    # Create database record
    db_file = UploadedFile(
        id=file_id,
        user_id=str(current_user.id),
        original_name=file.filename,
        file_path=stored_filename,  # Store relative path
        file_type=mime_type,
        file_size=file_size,
        extracted_content=extracted_content,
        conversation_id=conversation_id,
        file_metadata={
            "extension": ext,
            "uploaded_at": datetime.utcnow().isoformat()
        }
    )

    db.add(db_file)
    await db.commit()
    await db.refresh(db_file)

    return FileUploadResponse(
        id=db_file.id,
        original_name=db_file.original_name,
        file_type=db_file.file_type,
        file_size=db_file.file_size,
        created_at=db_file.created_at,
        extracted_content=db_file.extracted_content
    )


@router.get("/{file_id}", response_model=FileUploadResponse)
async def get_file(
    file_id: str,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get file metadata by ID."""
    from sqlalchemy import select

    result = await db.execute(select(UploadedFile).where(UploadedFile.id == file_id))
    db_file = result.scalar_one_or_none()

    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")

    # Check ownership
    if db_file.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to access this file")

    return FileUploadResponse(
        id=db_file.id,
        original_name=db_file.original_name,
        file_type=db_file.file_type,
        file_size=db_file.file_size,
        created_at=db_file.created_at,
        extracted_content=db_file.extracted_content
    )


@router.delete("/{file_id}")
async def delete_file(
    file_id: str,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete an uploaded file."""
    from sqlalchemy import select

    result = await db.execute(select(UploadedFile).where(UploadedFile.id == file_id))
    db_file = result.scalar_one_or_none()

    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")

    # Check ownership
    if db_file.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to delete this file")

    # Delete file from disk
    file_path = os.path.join(UPLOAD_DIR, db_file.file_path)
    if os.path.exists(file_path):
        os.remove(file_path)

    # Delete from database
    await db.delete(db_file)
    await db.commit()

    return {"message": "File deleted successfully"}
