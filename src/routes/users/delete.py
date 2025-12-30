from fastapi import APIRouter, Depends, HTTPException, status, Security
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.models.users import Users
from src.routes.deps import require_permission

router = APIRouter()


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _=Security(require_permission("administrator.delete"))
):
    user = await db.get(Users, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    await db.delete(user)
    await db.commit()
    
    return {"status": "ok", "message": "User deleted successfully", "user_id": user_id}
