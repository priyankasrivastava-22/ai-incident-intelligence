from fastapi import APIRouter

router = APIRouter(
    prefix="/api/v1",
    tags=["API v1"],
)


@router.get("/health")
async def health_check_v1():
    return {
        "status": "healthy",
        "version": "v1"
    }