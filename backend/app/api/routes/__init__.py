from .auth import auth_routes
from .admin import (
    user_management_routes,
    audit_routes,
    analytics_routes
)

# Create and include all routers
router = auth_routes.router
router.include_router(user_management_routes.router)
router.include_router(audit_routes.router)
router.include_router(analytics_routes.router)

__all__ = ["router"]