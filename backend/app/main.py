from fastapi import FastAPI
from app.api.routes import router as api_router
from app.ml.regression import train_model  # Ensure model is trained at startup

app = FastAPI()

@app.on_event("startup")
def startup_event():
    train_model()  

app.include_router(api_router)
