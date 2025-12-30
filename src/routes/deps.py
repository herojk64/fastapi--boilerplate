from typing import Optional
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from src.database.db import get_db
from src.models.users import Users
from src.utils.jwt import decode_access_token

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    cred: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> Users:
    """Authenticate using Bearer JWT; token must contain `user_id` claim."""
    if cred is None or cred.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid authorization header")
    token = cred.credentials
    try:
        payload = decode_access_token(token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token missing user_id")
    # eager load roles and permissions
    result = await db.execute(
        select(Users)
        .where(Users.id == int(user_id))
        .options(selectinload(Users.roles).selectinload(Users.roles.property.mapper.class_.permissions))
        .options(selectinload(Users.permissions))
    )
    user = result.scalars().first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


async def require_admin(current_user: Users = Depends(get_current_user)) -> Users:
    """Check if user has admin role (legacy check for compatibility)."""
    role_names = {r.name for r in current_user.roles}
    if "admin" not in role_names:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    return current_user


def require_permission(permission_name: str):
    """Return a dependency that checks if the current user has the specified permission."""
    async def _check_permission(current_user: Users = Depends(get_current_user)) -> Users:
        # collect permissions from roles and direct user permissions
        user_permissions = {p.name for p in current_user.permissions}
        for role in current_user.roles:
            user_permissions.update(p.name for p in role.permissions)
        
        if permission_name not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission_name}' required"
            )
        return current_user
    return _check_permission
