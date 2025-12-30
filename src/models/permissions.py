from typing import List
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Mapped, relationship
from src.database.db import Base
from src.models.role_permission import role_permissions
from src.models.user_permission import user_permissions


class Permissions(Base):
    __tablename__ = "permissions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255), nullable=True)

    roles:Mapped[List["Roles"]] = relationship("Roles", secondary=role_permissions, back_populates="permissions")
    users:Mapped[List["Users"]] = relationship("Users", secondary=user_permissions, back_populates="permissions")
