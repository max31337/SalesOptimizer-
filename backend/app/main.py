from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth import auth_routes
from app.api.admin import admin_routes, audit_routes, user_management
from app.api.auth import password_reset_routes  

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router, prefix="/api")
app.include_router(admin_routes.router, prefix="/api")
app.include_router(audit_routes.router, prefix="/api")
app.include_router(user_management.router, prefix="/api")
app.include_router(password_reset_routes.router, prefix="/api")