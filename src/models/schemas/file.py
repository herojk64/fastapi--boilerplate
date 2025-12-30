from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class FileUpload(BaseModel):
    """Schema for file upload."""
    access_level: str = "private"  # public, private, protected, admin, custom
    required_permission: Optional[str] = None
    role_ids: Optional[List[int]] = None
    permission_ids: Optional[List[int]] = None


class FileOut(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_path: str
    file_size: int
    mime_type: str
    access_level: str
    owner_id: int
    required_permission: Optional[str]
    is_active: bool
    download_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class FileUpdate(BaseModel):
    """Schema for updating file metadata."""
    access_level: Optional[str] = None
    required_permission: Optional[str] = None
    is_active: Optional[bool] = None
    role_ids: Optional[List[int]] = None
    permission_ids: Optional[List[int]] = None
