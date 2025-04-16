from fastapi import APIRouter
from .user_management_routes import router as user_management_router
from .audit_routes import router as audit_router 
from .analytics_routes import router as analytics_router

router = APIRouter()

# Include all admin sub-routes with proper prefixes
router.include_router(user_management_router, prefix="/users")
router.include_router(audit_router, prefix="/audit")
router.include_router(analytics_router, prefix="/analytics")

__all__ = ["router"]