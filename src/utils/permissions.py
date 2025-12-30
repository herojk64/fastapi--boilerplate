from typing import Optional, List
from src.models.users import Users


def check_file_access(
    user: Users,
    required_permission: Optional[str] = None,
    owner_id: Optional[int] = None,
    allow_owner: bool = True
) -> bool:
    """
    Check if user has access to a file.
    
    Args:
        user: Current user object
        required_permission: Permission name required to access file
        owner_id: ID of the file owner
        allow_owner: Whether file owner has automatic access
    
    Returns:
        bool: True if user has access, False otherwise
    """
    # Check if user is owner
    if allow_owner and owner_id and user.id == owner_id:
        return True
    
    # Check required permission
    if required_permission:
        return has_permission(user, required_permission)
    
    return False


def has_permission(user: Users, permission_name: str) -> bool:
    """Check if user has specific permission."""
    # Check direct permissions
    for perm in user.permissions:
        if perm.name == permission_name:
            return True
    
    # Check role permissions
    for role in user.roles:
        for perm in role.permissions:
            if perm.name == permission_name:
                return True
    
    return False


def has_any_permission(user: Users, permission_names: List[str]) -> bool:
    """Check if user has any of the specified permissions."""
    return any(has_permission(user, perm) for perm in permission_names)


def has_all_permissions(user: Users, permission_names: List[str]) -> bool:
    """Check if user has all of the specified permissions."""
    return all(has_permission(user, perm) for perm in permission_names)


def is_admin(user: Users) -> bool:
    """Check if user has administrator role."""
    return any(role.name == "Administrator" for role in user.roles)
