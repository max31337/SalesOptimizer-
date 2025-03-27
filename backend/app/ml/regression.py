import joblib
import numpy as np
import os
from sklearn.linear_model import LinearRegression

MODEL_DIR = "storage/saved_models"
MODEL_PATH = os.path.join(MODEL_DIR, "sales_model.pkl")

def train_model():
    """Train a simple regression model and save it"""
    
    # Dummy training data
    X = np.array([[1], [2], [3], [4], [5], [6]])
    y = np.array([10, 20, 30, 40, 50, 60])

    model = LinearRegression()
    model.fit(X, y)

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"✅ Model saved at {MODEL_PATH}")

def predict_sales(value: float):
    """Load trained model and predict sales"""
    
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("❌ Model file not found. Please train the model first.")

    model = joblib.load(MODEL_PATH)

    prediction = model.predict(np.array([[value]]))

    return float(prediction[0])  