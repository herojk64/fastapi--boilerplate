#!/usr/bin/env python
"""Seeder for default roles, permissions, and admin user.

Run: `poetry run python scripts/seed_admin.py` or set env vars and run.
"""
import os
import asyncio
from sqlalchemy import text, select

from src.database.db import async_session
from src.services.authorization import (
    get_role_by_name,
    get_permission_by_name,
)
from src.models.users import Users
from src.models.roles import Roles
from src.models.permissions import Permissions
from src.models.role_permission import role_permissions
from src.utils.security import hash_password


ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")

DEFAULT_PERMISSIONS = [
    ("administrator.create", "Admin can create resources"),
    ("administrator.read", "Admin can read resources"),
    ("administrator.update", "Admin can update resources"),
    ("administrator.delete", "Admin can delete resources"),
]


async def main():
    async with async_session() as session:
        async with session.begin():
            # create default permissions
            for perm_name, perm_desc in DEFAULT_PERMISSIONS:
                existing = await get_permission_by_name(session, perm_name)
                if not existing:
                    perm = Permissions(name=perm_name, description=perm_desc)
                    session.add(perm)
                    await session.flush()
                    print(f"Created permission: {perm_name}")

            # create admin role and assign permissions
            result_role = await session.execute(select(Roles).where(Roles.name == "admin"))
            admin_role = result_role.scalars().first()
            if not admin_role:
                admin_role = Roles(name="admin", description="Administrator role with full permissions")
                session.add(admin_role)
                await session.flush()
                await session.refresh(admin_role)
                print("Created admin role")

            # assign all admin permissions to admin role
            for perm_name, _ in DEFAULT_PERMISSIONS:
                perm = await get_permission_by_name(session, perm_name)
                if perm:
                    # check if permission is already assigned
                    result_check = await session.execute(
                        select(1)
                        .select_from(role_permissions)
                        .where(
                            (role_permissions.c.role_id == admin_role.id) &
                            (role_permissions.c.permission_id == perm.id)
                        )
                    )
                    if not result_check.scalar():
                        # insert directly into the association table
                        await session.execute(
                            role_permissions.insert().values(
                                role_id=admin_role.id,
                                permission_id=perm.id
                            )
                        )
                        print(f"Assigned {perm_name} to admin role")

            # create admin user if not exists
            result = await session.execute(
                text("SELECT id FROM users WHERE email = :email"),
                {"email": ADMIN_EMAIL},
            )
            row = result.first()
            if row:
                print("Admin user already exists, skipping creation")
                return

            admin = Users(email=ADMIN_EMAIL, username=ADMIN_USERNAME, password_hash=hash_password(ADMIN_PASSWORD))
            session.add(admin)
            await session.flush()
            await session.refresh(admin)

            # assign admin role to user - insert directly into association table
            from src.models.user_role import user_roles
            await session.execute(
                user_roles.insert().values(
                    user_id=admin.id,
                    role_id=admin_role.id
                )
            )
            print(f"Created admin user {ADMIN_EMAIL} with username {ADMIN_USERNAME} and admin role")


if __name__ == "__main__":
    asyncio.run(main())
