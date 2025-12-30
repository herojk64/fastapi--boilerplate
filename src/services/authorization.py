from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from src.models.roles import Roles
from src.models.permissions import Permissions
from src.models.users import Users

logger = logging.getLogger(__name__)


def _ensure_async_session(session):
    if not isinstance(session, AsyncSession):
        raise RuntimeError(f"Expected AsyncSession, got {type(session)}. Ensure this function is called from async context with an AsyncSession.")


async def create_role(session: AsyncSession, name: str, description: Optional[str] = None) -> Roles:
    _ensure_async_session(session)
    role = Roles(name=name, description=description)
    session.add(role)
    await session.flush()
    await session.refresh(role)
    return role


async def get_role_by_name(session: AsyncSession, name: str) -> Optional[Roles]:
    _ensure_async_session(session)
    result = await session.execute(select(Roles).where(Roles.name == name))
    return result.scalars().first()


async def list_roles(session: AsyncSession) -> List[Roles]:
    _ensure_async_session(session)
    result = await session.execute(select(Roles))
    return result.scalars().all()


async def create_permission(session: AsyncSession, name: str, description: Optional[str] = None) -> Permissions:
    _ensure_async_session(session)
    perm = Permissions(name=name, description=description)
    session.add(perm)
    await session.flush()
    await session.refresh(perm)
    return perm


async def get_permission_by_name(session: AsyncSession, name: str) -> Optional[Permissions]:
    _ensure_async_session(session)
    result = await session.execute(select(Permissions).where(Permissions.name == name))
    return result.scalars().first()


async def list_permissions(session: AsyncSession) -> List[Permissions]:
    _ensure_async_session(session)
    result = await session.execute(select(Permissions))
    return result.scalars().all()


async def assign_role_to_user(session: AsyncSession, user_id: int, role_id: int) -> Users:
    _ensure_async_session(session)
    user = await session.get(Users, user_id)
    role = await session.get(Roles, role_id)
    if user is None or role is None:
        raise ValueError("User or Role not found")
    if role not in user.roles:
        user.roles.append(role)
        session.add(user)
    await session.flush()
    await session.refresh(user)
    return user


async def assign_permission_to_role(session: AsyncSession, role_id: int, permission_id: int) -> Roles:
    _ensure_async_session(session)
    try:
        role = await session.get(Roles, role_id)
        perm = await session.get(Permissions, permission_id)
        if role is None or perm is None:
            raise ValueError("Role or Permission not found")
        if perm not in role.permissions:
            role.permissions.append(perm)
            session.add(role)
        await session.flush()
        await session.refresh(role)
        return role
    except Exception as e:
        logger.exception("Error assigning permission to role")
        raise


async def assign_permission_to_user(session: AsyncSession, user_id: int, permission_id: int) -> Users:
    _ensure_async_session(session)
    user = await session.get(Users, user_id)
    perm = await session.get(Permissions, permission_id)
    if user is None or perm is None:
        raise ValueError("User or Permission not found")
    if perm not in user.permissions:
        user.permissions.append(perm)
        session.add(user)
    await session.flush()
    await session.refresh(user)
    return user
