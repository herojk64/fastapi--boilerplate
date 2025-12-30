from fastapi import APIRouter, Depends, HTTPException, status, Security
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.models.users import Users
from src.models.schemas.user import UserOut, UserUpdate
from src.routes.deps import require_permission
from src.utils.security import hash_password

router = APIRouter()


@router.put("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    _=Security(require_permission("administrator.update"))
):
    user = await db.get(Users, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Update fields if provided
    update_data = user_data.model_dump(exclude_unset=True)
    
    # Handle password separately
    if "password" in update_data:
        user.password_hash = hash_password(update_data.pop("password"))
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return user
