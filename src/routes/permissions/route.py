from fastapi import APIRouter, Depends, HTTPException, status, Security, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from pydantic import BaseModel

from src.database.db import get_db
from src.models.schemas.permission import PermissionCreate, PermissionOut
from src.models.permissions import Permissions
from src.services.authorization import (
	create_permission,
	assign_permission_to_role,
	assign_permission_to_user,
)

from src.routes.deps import require_admin, require_permission


class PaginatedPermissions(BaseModel):
    items: List[PermissionOut]
    total: int
    page: int
    page_size: int
    total_pages: int


router = APIRouter(prefix="/permissions", tags=["Permissions"])


@router.post("/", response_model=PermissionOut, status_code=status.HTTP_201_CREATED)
async def create_permission_endpoint(
    permission: PermissionCreate,
    db: AsyncSession = Depends(get_db),
    _=Security(require_permission("administrator.create"))
):
	try:
		created = await create_permission(db, permission.name, permission.description)
		return created
	except Exception as e:
		import logging, traceback
		logging.getLogger(__name__).exception("Failed to create permission")
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Create permission error: {e}")


@router.get("/", response_model=PaginatedPermissions)
async def list_permissions_endpoint(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db)
):
	# Get total count
	count_result = await db.execute(select(func.count(Permissions.id)))
	total = count_result.scalar()
	
	# Get paginated permissions
	offset = (page - 1) * page_size
	result = await db.execute(
	    select(Permissions)
	    .offset(offset)
	    .limit(page_size)
	)
	permissions = result.scalars().all()
	
	total_pages = (total + page_size - 1) // page_size
	
	return PaginatedPermissions(
	    items=permissions,
	    total=total,
	    page=page,
	    page_size=page_size,
	    total_pages=total_pages
	)


@router.post("/role/{role_id}/assign/{permission_id}")
async def assign_perm_to_role(
    role_id: int,
    permission_id: int,
    db: AsyncSession = Depends(get_db),
    _=Security(require_permission("administrator.update"))
):
	try:
		role = await assign_permission_to_role(db, role_id, permission_id)
		return {"status": "ok", "role_id": role.id}
	except ValueError as e:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
	except Exception as e:
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/user/{user_id}/assign/{permission_id}")
async def assign_perm_to_user(
    user_id: int,
    permission_id: int,
    db: AsyncSession = Depends(get_db),
    _=Security(require_permission("administrator.update"))
):
	try:
		user = await assign_permission_to_user(db, user_id, permission_id)
		return {"status": "ok", "user_id": user.id}
	except ValueError as e:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
	except Exception as e:
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

