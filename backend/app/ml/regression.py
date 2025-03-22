import os
import joblib
import numpy as np
from sklearn.linear_model import LinearRegression

MODEL_DIR = "backend/app/ml"
MODEL_PATH = os.path.join(MODEL_DIR, "sales_model.pkl")

def train_model():
    os.makedirs(MODEL_DIR, exist_ok=True)

    X_train = np.array([[1], [2], [3], [4], [5]])
    y_train = np.array([10, 20, 30, 40, 50])

    model = LinearRegression()
    model.fit(X_train, y_train)

    joblib.dump(model, MODEL_PATH)
    print(f"✅ Model trained and saved at: {MODEL_PATH}")

if __name__ == "__main__":
    train_model()
