import secrets
from datetime import datetime, timedelta
import jwt
from app.core.config import settings  # Updated import

# Add this function to token.py
def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt

def generate_verification_token() -> str:
    return secrets.token_urlsafe(32)

def create_verification_token(email: str) -> str:
    expiration = datetime.utcnow() + timedelta(hours=24)
    return jwt.encode(
        {"email": email, "exp": expiration},
        settings.SECRET_KEY,  # Updated to use settings
        algorithm=settings.ALGORITHM  # Updated to use settings
    )

def verify_token(token: str) -> str:
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY,  # Updated to use settings
            algorithms=[settings.ALGORITHM]  # Updated to use settings
        )
        return payload["email"]
    except jwt.ExpiredSignatureError:
        return None
    except jwt.JWTError:
        return None