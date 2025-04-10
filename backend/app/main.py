from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth import auth_routes
from app.api.admin import admin_routes, audit_routes, user_management
from app.api.auth import password_reset_routes  
from app.api.admin.analytics_routes import router as analytics_router
from app.core.config import SECRET_KEY
from app.api.crm import customer_routes
from app.api.crm import interaction_routes  # Add this import
from app.api.admin.user_management import router as admin_user_router
from app.core.environment import get_settings

app = FastAPI()

# Add this health check endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

from app.core.environment import get_settings

settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router, prefix="/api")
app.include_router(admin_routes.router, prefix="/api")
app.include_router(audit_routes.router, prefix="/api")
app.include_router(user_management.router, prefix="/api")
app.include_router(password_reset_routes.router, prefix="/api")
app.include_router(analytics_router, prefix="/api", tags=["analytics"])
app.include_router(customer_routes.router, prefix="/api/crm", tags=["crm"])
app.include_router(interaction_routes.router, prefix="/api/crm")
app.include_router(admin_user_router, prefix="/api")