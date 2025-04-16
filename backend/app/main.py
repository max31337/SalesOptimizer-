from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.middleware.error_handler import error_handler
from app.api.routes import router as api_router
from app.api.routes.admin.admin_routes import router as admin_router
from app.api.routes.auth.auth_routes import router as auth_router
from app.api.routes.auth.user_check_routes import router as check_router
from app.api.routes import (
    user_management_routes,
    audit_routes,
    analytics_routes
)

# Update your FastAPI initialization to include version prefix
app = FastAPI()

# Add error handler middleware
app.middleware("http")(error_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simplified route inclusion
# Remove duplicate route inclusions and update the admin router prefix
app.include_router(api_router, prefix="/api")
app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])
app.include_router(check_router, prefix="/api/auth", tags=["authentication"])
app.include_router(admin_router, prefix="/api/admin", tags=["Admin"])
