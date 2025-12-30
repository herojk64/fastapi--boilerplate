from fastapi import APIRouter, Depends, HTTPException, status, Security, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List

from src.database.db import get_db
from src.models.users import Users
from src.models.schemas.user import UserOut
from src.routes.deps import require_permission
from pydantic import BaseModel

router = APIRouter()


class PaginatedUsers(BaseModel):
    items: List[UserOut]
    total: int
    page: int
    page_size: int
    total_pages: int


@router.get("/", response_model=PaginatedUsers)
async def get_all_users(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    _=Security(require_permission("administrator.read"))
):
    # Get total count
    count_result = await db.execute(select(func.count(Users.id)))
    total = count_result.scalar()
    
    # Get paginated users
    offset = (page - 1) * page_size
    result = await db.execute(
        select(Users)
        .offset(offset)
        .limit(page_size)
    )
    users = result.scalars().all()
    
    total_pages = (total + page_size - 1) // page_size
    
    return PaginatedUsers(
        items=users,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{user_id}", response_model=UserOut)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _=Security(require_permission("administrator.read"))
):
    user = await db.get(Users, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
