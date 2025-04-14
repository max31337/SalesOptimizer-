from fastapi import APIRouter
from .user_management_routes import router as user_management_router
from .analytics_routes import router as analytics_router
from .audit_routes import router as audit_router

# All admin routes will have prefix /api/admin/
router = APIRouter(prefix="/admin", tags=["Admin"])

router.include_router(user_management_router)
router.include_router(analytics_router)
router.include_router(audit_router) 