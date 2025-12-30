"""Model package initializer — import models to register them with SQLAlchemy.

Importing this package will import all model modules so declarative mappers
are configured and relationship string lookups (e.g. "Roles") can be resolved.
"""
from .users import Users
from .roles import Roles
from .permissions import Permissions
from .files import File, FilePermission, FileRole

from .user_role import user_roles
from .user_permission import user_permissions
from .role_permission import role_permissions

__all__ = [
    "Users",
    "Roles",
    "Permissions",
    "File",
    "FilePermission",
    "FileRole",
    "user_roles",
    "user_permissions",
    "role_permissions",
]
