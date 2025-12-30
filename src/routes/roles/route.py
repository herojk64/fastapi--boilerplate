from fastapi import APIRouter, Depends, HTTPException, status, Security, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from pydantic import BaseModel

from src.database.db import get_db
from src.models.schemas.role import RoleCreate, RoleOut
from src.models.roles import Roles
from src.services.authorization import (
	create_role,
	get_role_by_name,
	assign_role_to_user,
)

from src.routes.deps import require_admin, require_permission


class PaginatedRoles(BaseModel):
    items: List[RoleOut]
    total: int
    page: int
    page_size: int
    total_pages: int


router = APIRouter(prefix="/roles", tags=["Roles"])


@router.post("/", response_model=RoleOut, status_code=status.HTTP_201_CREATED)
async def create_role_endpoint(
    role: RoleCreate,
    db: AsyncSession = Depends(get_db),
    _=Security(require_permission("administrator.create"))
):
	existing = await get_role_by_name(db, role.name)
	if existing:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role already exists")
	created = await create_role(db, role.name, role.description)
	return created


@router.get("/", response_model=PaginatedRoles)
async def list_roles_endpoint(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db)
):
	# Get total count
	count_result = await db.execute(select(func.count(Roles.id)))
	total = count_result.scalar()
	
	# Get paginated roles
	offset = (page - 1) * page_size
	result = await db.execute(
	    select(Roles)
	    .offset(offset)
	    .limit(page_size)
	)
	roles = result.scalars().all()
	
	total_pages = (total + page_size - 1) // page_size
	
	return PaginatedRoles(
	    items=roles,
	    total=total,
	    page=page,
	    page_size=page_size,
	    total_pages=total_pages
	)


@router.post("/{role_id}/assign/{user_id}")
async def assign_role(
    role_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _=Security(require_permission("administrator.update"))
):
	try:
		user = await assign_role_to_user(db, user_id, role_id)
		return {"status": "ok", "user_id": user.id}
	except ValueError as e:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
	except Exception as e:
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

