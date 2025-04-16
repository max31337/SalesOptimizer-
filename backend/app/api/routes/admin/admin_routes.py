from fastapi import APIRouter
from .user_management_routes import router as user_mgmt_router
from .analytics_routes import router as analytics_router
from .audit_routes import router as audit_router

router = APIRouter()
router.include_router(user_mgmt_router)
router.include_router(analytics_router)
router.include_router(audit_router)

__all__ = ["router"]