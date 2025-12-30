from fastapi import APIRouter, Depends, HTTPException, status, Security
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.routes.deps import get_current_user
from src.models.schemas.user import UserOut
from pydantic import BaseModel
from src.utils.security import verify_password, hash_password


class PasswordChangeIn(BaseModel):
    old_password: str
    new_password: str


router = APIRouter(prefix="/profile", tags=["Users"])


@router.get("/", response_model=UserOut)
async def get_profile(current_user=Security(get_current_user)):
    return current_user


@router.put("/password")
async def change_password(data: PasswordChangeIn, db: AsyncSession = Depends(get_db), current_user=Security(get_current_user)):
    # verify old password
    if not verify_password(data.old_password, current_user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Old password is incorrect")
    # update password
    current_user.password_hash = hash_password(data.new_password)
    db.add(current_user)
    await db.commit()
    return {"status": "ok"}
