from fastapi import APIRouter, HTTPException, UploadFile, File as FastAPIFile, Depends, status, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from pathlib import Path
from typing import List, Optional
import os

from src.database.db import get_db
from src.routes.deps import get_current_user
from src.models.users import Users
from src.models.files import File
from src.models.schemas.file import FileOut, FileUpdate
from src.utils.files import save_upload_file, delete_file as delete_file_util

router = APIRouter(prefix="/files", tags=["Files"])


@router.post("/upload", response_model=FileOut, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    access_level: str = Query("private", description="public or private"),
    required_permission: Optional[str] = Query(None, description="Required permission for private files"),
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """
    Upload a file.
    
    - Public files: Accessible via /storage/filename (no auth)
    - Private files: Accessible via /api/v1/files/{file_id} (with auth + permission check)
    """
    file_metadata = await save_upload_file(
        file,
        directory=f"user_{current_user.id}",
        public=(access_level == "public"),
        owner_id=current_user.id
    )
    
    db_file = File(
        filename=file_metadata["relative_path"].split("/")[-1],
        original_filename=file_metadata["filename"],
        file_path=file_metadata["relative_path"],
        file_size=file_metadata["size"],
        mime_type=file_metadata["content_type"],
        access_level=access_level,
        owner_id=current_user.id,
        required_permission=required_permission
    )
    
    db.add(db_file)
    await db.commit()
    await db.refresh(db_file)
    
    return db_file


@router.get("/", response_model=List[FileOut])
async def list_my_files(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """List your uploaded files."""
    offset = (page - 1) * page_size
    
    result = await db.execute(
        select(File)
        .where(File.owner_id == current_user.id)
        .where(File.is_active == True)
        .offset(offset)
        .limit(page_size)
    )
    return result.scalars().all()


@router.get("/{file_id}")
async def get_file(
    file_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Get a private file with permission check."""
    result = await db.execute(select(File).where(File.id == file_id))
    file = result.scalar_one_or_none()
    
    if not file or not file.is_active:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Owner always has access
    if file.owner_id == current_user.id:
        pass
    # Check required permission if set
    elif file.required_permission:
        has_permission = any(
            perm.name == file.required_permission 
            for perm in current_user.permissions
        ) or any(
            perm.name == file.required_permission
            for role in current_user.roles
            for perm in role.permissions
        )
        if not has_permission:
            raise HTTPException(status_code=403, detail=f"Permission '{file.required_permission}' required")
    else:
        raise HTTPException(status_code=403, detail="Access denied")
    
    storage_path = Path(os.getcwd()) / "storage" / "private" / file.file_path
    
    if not storage_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    file.download_count += 1
    await db.commit()
    
    return FileResponse(storage_path, filename=file.original_filename)


@router.patch("/{file_id}", response_model=FileOut)
async def update_file(
    file_id: int,
    file_update: FileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Update file settings (owner only)."""
    result = await db.execute(select(File).where(File.id == file_id))
    file = result.scalar_one_or_none()
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    if file.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if file_update.access_level:
        file.access_level = file_update.access_level
    if file_update.required_permission is not None:
        file.required_permission = file_update.required_permission
    if file_update.is_active is not None:
        file.is_active = file_update.is_active
    
    await db.commit()
    await db.refresh(file)
    
    return file


@router.delete("/{file_id}")
async def delete_file(
    file_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Delete file (owner only)."""
    result = await db.execute(select(File).where(File.id == file_id))
    file = result.scalar_one_or_none()
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    if file.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    delete_file_util(file.file_path, public=(file.access_level == "public"))
    await db.execute(delete(File).where(File.id == file_id))
    await db.commit()
    
    return {"message": "File deleted"}
