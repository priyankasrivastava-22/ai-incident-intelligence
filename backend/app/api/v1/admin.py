from fastapi import APIRouter, Depends

from backend.app.core.dependencies import require_admin
from backend.app.models.user import User


router = APIRouter(
    prefix="/admin",
    tags=["Administration"],
)


@router.get("/test")
def admin_test(
    current_user: User = Depends(require_admin),
):
    """Verify that the current user has administrator access."""
    return {
        "status": "authorized",
        "message": "Admin access granted.",
        "user_id": str(current_user.id),
        "role": current_user.role,
    }