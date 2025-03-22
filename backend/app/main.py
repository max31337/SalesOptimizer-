from fastapi import FastAPI
from app.api.routes import router as api_router

app = FastAPI()

app.include_router(api_router)

@app.get("/")
def home():
    return {"message": "Welcome to SalesOptimizer API!"}
