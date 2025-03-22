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
