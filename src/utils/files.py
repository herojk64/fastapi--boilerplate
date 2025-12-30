import os
import uuid
import mimetypes
from pathlib import Path
from typing import Optional, List
from fastapi import UploadFile, HTTPException


ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
ALLOWED_DOCUMENT_TYPES = {"application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def get_storage_path(public: bool = True) -> Path:
    """Get the storage directory path."""
    base = Path(os.getcwd()) / "storage"
    return base / "public" if public else base / "private"


def generate_unique_filename(original_filename: str) -> str:
    """Generate a unique filename while preserving extension."""
    ext = Path(original_filename).suffix
    return f"{uuid.uuid4()}{ext}"


def validate_file_type(file: UploadFile, allowed_types: set) -> None:
    """Validate file MIME type."""
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(allowed_types)}"
        )


def validate_file_size(file: UploadFile, max_size: int = MAX_FILE_SIZE) -> None:
    """Validate file size."""
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    if file_size > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {max_size / (1024 * 1024):.1f}MB"
        )


async def save_upload_file(
    file: UploadFile,
    directory: str = "",
    public: bool = True,
    allowed_types: Optional[set] = None,
    max_size: int = MAX_FILE_SIZE,
    owner_id: Optional[int] = None
) -> dict:
    """
    Save uploaded file and return file metadata.
    
    Returns:
        dict: {
            'filename': str,
            'relative_path': str,
            'size': int,
            'content_type': str,
            'owner_id': Optional[int]
        }
    """
    if allowed_types:
        validate_file_type(file, allowed_types)
    
    validate_file_size(file, max_size)
    
    # Generate unique filename
    unique_name = generate_unique_filename(file.filename or "file")
    
    # Construct full path
    storage_path = get_storage_path(public)
    if directory:
        storage_path = storage_path / directory
        storage_path.mkdir(parents=True, exist_ok=True)
    
    file_path = storage_path / unique_name
    
    # Save file
    content = await file.read()
    with open(file_path, "wb") as buffer:
        buffer.write(content)
    
    # Return relative path and metadata
    relative_path = f"{directory}/{unique_name}" if directory else unique_name
    return {
        "filename": file.filename or "file",
        "relative_path": relative_path,
        "size": len(content),
        "content_type": file.content_type or "application/octet-stream",
        "owner_id": owner_id
    }


def delete_file(relative_path: str, public: bool = True) -> bool:
    """Delete a file from storage."""
    storage_path = get_storage_path(public)
    file_path = storage_path / relative_path
    
    try:
        if file_path.exists():
            file_path.unlink()
            return True
        return False
    except Exception:
        return False


def get_file_url(
    relative_path: str,
    access_level: str = "public",
    base_url: str = "http://localhost:3000"
) -> str:
    """
    Generate URL for a file based on access level.
    
    Args:
        relative_path: File path relative to storage directory
        access_level: 'public', 'private', 'protected', or 'admin'
        base_url: Base URL of the application
    """
    if access_level == "public":
        return f"{base_url}/storage/{relative_path}"
    elif access_level == "private":
        return f"{base_url}/api/v1/files/private/{relative_path}"
    elif access_level == "protected":
        return f"{base_url}/api/v1/files/protected/{relative_path}"
    elif access_level == "admin":
        return f"{base_url}/api/v1/files/admin/{relative_path}"
    else:
        return f"{base_url}/api/v1/files/private/{relative_path}"


def validate_image(file: UploadFile) -> None:
    """Validate image file type."""
    validate_file_type(file, ALLOWED_IMAGE_TYPES)


def validate_document(file: UploadFile) -> None:
    """Validate document file type."""
    validate_file_type(file, ALLOWED_DOCUMENT_TYPES)


def get_file_extension(filename: str) -> str:
    """Get file extension from filename."""
    return Path(filename).suffix.lower()


def get_mime_type(filename: str) -> str:
    """Get MIME type from filename."""
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type or "application/octet-stream"


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def is_image(filename: str) -> bool:
    """Check if file is an image based on extension."""
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg'}
    return get_file_extension(filename) in image_extensions


def is_video(filename: str) -> bool:
    """Check if file is a video based on extension."""
    video_extensions = {'.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv'}
    return get_file_extension(filename) in video_extensions


def is_audio(filename: str) -> bool:
    """Check if file is audio based on extension."""
    audio_extensions = {'.mp3', '.wav', '.ogg', '.flac', '.aac', '.m4a'}
    return get_file_extension(filename) in audio_extensions


def is_document(filename: str) -> bool:
    """Check if file is a document based on extension."""
    doc_extensions = {'.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.xls', '.xlsx', '.ppt', '.pptx'}
    return get_file_extension(filename) in doc_extensions


def sanitize_path(path: str) -> str:
    """Sanitize file path to prevent directory traversal."""
    # Remove any .. or absolute paths
    clean_path = Path(path).as_posix()
    if '..' in clean_path or clean_path.startswith('/'):
        raise HTTPException(status_code=400, detail="Invalid file path")
    return clean_path
