import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import your routers
from app.api.routes.auth import auth_routes, invited_user_routes, password_reset_routes, user_check_routes # Add invited_user_routes
from app.api.routes.admin import user_management_routes, audit_routes # Example admin routes

app = FastAPI(title="SalesOptimizer API")

# CORS Middleware Configuration
origins = [
    "http://localhost:5500",  # frontend development server
    "http://127.0.0.1:5500",
    "https://salesoptimizer.vercel.app", # production frontend
    # Add any other origins as needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(auth_routes.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(invited_user_routes.router, prefix="/api/auth", tags=["Invited User"]) # Add this line
app.include_router(password_reset_routes.router, prefix="/api/auth", tags=["Password Reset"]) # Example
app.include_router(user_check_routes.router, prefix="/api/auth", tags=["User Check"]) # Example

# Include Admin Routers 
app.include_router(user_management_routes.router, prefix="/api/admin", tags=["Admin - User Management"])
app.include_router(audit_routes.router, prefix="/api/admin", tags=["Admin - Audit Logs"])

@app.get("/")
def read_root():
    return {"message": "Welcome to SalesOptimizer API"}

# Add this if you want to run directly with python main.py (optional)
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)