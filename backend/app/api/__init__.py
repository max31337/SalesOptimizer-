from fastapi import APIRouter
from .routes.auth.auth_routes import router as auth_router
from .routes.auth.invited_user_routes import router as invited_user_router
from .routes.admin.user_management_routes import router as admin_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/api/auth", tags=["auth"])
api_router.include_router(invited_user_router, prefix="/api/auth", tags=["auth"])
api_router.include_router(admin_router, prefix="/api/admin", tags=["admin"])
