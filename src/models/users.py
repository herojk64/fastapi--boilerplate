from typing import List
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    func,
)
from sqlalchemy.orm import Mapped, relationship
from src.database.db import Base
from src.models.user_role import user_roles
from src.models.user_permission import user_permissions


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # --- Auth fields ---
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=True)  # optional

    # --- Basic profile (optional) ---
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)

    # --- Status ---
    is_active = Column(Boolean, default=True, nullable=False)

    # --- Timestamps ---
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    roles: Mapped[List["Roles"]] = relationship("Roles", secondary=user_roles, back_populates="users")
    permissions: Mapped[List["Permissions"]] = relationship("Permissions", secondary=user_permissions, back_populates="users")
    files: Mapped[List["File"]] = relationship("File", back_populates="owner")

    @property
    def fullname(self) -> str:
        parts = [self.first_name, self.last_name]
        return " ".join(map(str,filter(None, parts)))
