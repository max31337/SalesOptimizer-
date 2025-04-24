from fastapi import APIRouter
from .admin import user_management_routes, audit_routes, analytics_routes
from .auth import auth_routes, invited_user_routes, password_reset_routes, user_check_routes
from .crm import router as crm_router

router = APIRouter()

# Include all route modules
router.include_router(auth_routes.router, prefix="/auth", tags=["authentication"])
router.include_router(user_check_routes.router, prefix="/auth", tags=["authentication"])
router.include_router(invited_user_routes.router, prefix="/auth", tags=["authentication"])
router.include_router(password_reset_routes.router, prefix="/auth", tags=["authentication"])

# Admin routes
router.include_router(user_management_routes.router, prefix="/admin", tags=["admin"])
router.include_router(audit_routes.router, prefix="/admin", tags=["admin"])
router.include_router(analytics_routes.router, prefix="/admin", tags=["admin"])

# CRM routes
router.include_router(crm_router, prefix="/crm")