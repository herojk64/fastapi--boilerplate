from typing import List
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Mapped, relationship
from src.database.db import Base
from src.models.user_role import user_roles
from src.models.role_permission import role_permissions

class Roles(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255), nullable=True)

    users: Mapped[List["Users"]] = relationship("Users", secondary=user_roles, back_populates="roles")
    permissions: Mapped[List["Permissions"]] = relationship("Permissions", secondary=role_permissions, back_populates="roles")
