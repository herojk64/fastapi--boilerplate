from .auth.route import router as auth_router
from .users.route import router as users_router
from .roles.route import router as roles_router
from .permissions.route import router as permissions_router
from .files.route import router as files_router

REGISTERED_ROUTERS = [
    users_router,
    roles_router,
    permissions_router,
    auth_router,
    files_router,
]
