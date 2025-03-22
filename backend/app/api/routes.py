from fastapi import APIRouter, Depends
import psycopg2
import os
from dotenv import load_dotenv
from app.ml.regression import predict_sales  

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

router = APIRouter()

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

@router.get("/predict/")
def get_user_prediction(user_id: int, value: float):
    """Fetch user details and return sales prediction"""

    cursor.execute("SELECT name, email FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()

    if not user:
        return {"error": "User not found"}

    user_name, user_email = user

    predicted_sales = predict_sales(value)

    return {
        "user": {
            "id": user_id,
            "name": user_name,
            "email": user_email
        },
        "sales_prediction": {
            "input_value": value,
            "predicted_sales": predicted_sales
        }
    }
