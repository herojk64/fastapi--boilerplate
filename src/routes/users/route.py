from fastapi import APIRouter
from .create import router as create_router
from .read import router as read_router
from .update import router as update_router
from .delete import router as delete_router
from .profile import router as profile_router

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)

router.include_router(create_router)
router.include_router(read_router)
router.include_router(update_router)
router.include_router(delete_router)
router.include_router(profile_router)

