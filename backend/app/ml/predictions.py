import joblib
import numpy as np
import os

MODEL_DIR = "storage/saved_models"
MODEL_PATH = os.path.join(MODEL_DIR, "sales_model.pkl")

def predict_sales(value: float):
    """Load trained model and predict sales"""
    
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("❌ Model file not found. Please train the model first.")

    # Load trained model
    model = joblib.load(MODEL_PATH)

    # Predict sales
    prediction = model.predict(np.array([[value]]))

    return float(prediction[0])  
