from fastapi import APIRouter
from app.ml.predictions import predict_sales

router = APIRouter()

@router.get("/")
def home():
    return {"message": "Welcome to SalesOptimizer API!"}

@router.get("/predict/")
def get_prediction(value: float):
    """Predict sales based on input value"""
    prediction = predict_sales(value)
    return {"input": value, "predicted_sales": prediction}
