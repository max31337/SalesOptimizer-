import joblib
import numpy as np
import os

MODEL_PATH = "backend/app/ml/sales_model.pkl"

def predict_sales(value: float):
    """Load trained model and predict sales"""
    if not os.path.exists(MODEL_PATH):
        return "Model file not found. Train the model first."

    model = joblib.load(MODEL_PATH)
    
    prediction = model.predict(np.array([[value]]))
    return float(prediction[0])  
