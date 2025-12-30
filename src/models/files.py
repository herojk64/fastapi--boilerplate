from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, BigInteger, func
from sqlalchemy.orm import relationship
from src.database.db import Base


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False, unique=True)
    file_size = Column(BigInteger, nullable=False)
    mime_type = Column(String, nullable=False)
    
    # Access control
    access_level = Column(String, default="private")  # public, private, protected, admin, custom
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    required_permission = Column(String, nullable=True)  # e.g., "files.download", "documents.view"
    
    # Metadata
    is_active = Column(Boolean, default=True)
    download_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    owner = relationship("Users", back_populates="files", foreign_keys=[owner_id])


class FilePermission(Base):
    """Many-to-many relationship between files and permissions."""
    __tablename__ = "file_permissions"

    file_id = Column(Integer, ForeignKey("files.id", ondelete="CASCADE"), primary_key=True)
    permission_id = Column(Integer, ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True)


class FileRole(Base):
    """Many-to-many relationship between files and roles."""
    __tablename__ = "file_roles"

    file_id = Column(Integer, ForeignKey("files.id", ondelete="CASCADE"), primary_key=True)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
