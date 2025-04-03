from fastapi import FastAPI
from app.api.auth import auth_routes
from app.api.admin import admin_routes
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with prefix
app.include_router(auth_routes.router, prefix="/api")
app.include_router(admin_routes.router, prefix="/api")  # Make sure this line exists