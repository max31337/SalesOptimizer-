from fastapi import APIRouter
from .auth_routes import router as auth_router
from .invited_user_routes import router as invited_user_router 
from .user_check_routes import router as user_check_router
from .password_reset_routes import router as password_reset_router

router = APIRouter(tags=["Authentication"], prefix="/api/auth")

router.include_router(auth_router)
router.include_router(invited_user_router)
router.include_router(user_check_router)
router.include_router(password_reset_router)