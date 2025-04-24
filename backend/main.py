import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router  # Simplified import

app = FastAPI(title="SalesOptimizer API")

# CORS Middleware Configuration
origins = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "https://salesoptimizer.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routes through the main router
app.include_router(api_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to SalesOptimizer API"}

# Add this if you want to run directly with python main.py (optional)
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)