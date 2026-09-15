from fastapi import APIRouter

from backend.app.api.v1.admin import router as admin_router
from backend.app.api.v1.auth import router as auth_router
from backend.app.api.v1.logs import router as logs_router


router = APIRouter(
    prefix="/api/v1",
)


router.include_router(auth_router)
router.include_router(admin_router)
router.include_router(logs_router)


@router.get("/health")
async def health_check_v1():
    return {
        "status": "healthy",
        "version": "v1",
    }