import secrets
from datetime import datetime, timedelta
import jwt
from app.core.config import SECRET_KEY

def generate_verification_token() -> str:
    return secrets.token_urlsafe(32)

def create_verification_token(email: str) -> str:
    expiration = datetime.utcnow() + timedelta(hours=24)
    return jwt.encode(
        {"email": email, "exp": expiration},
        SECRET_KEY,
        algorithm="HS256"
    )

def verify_token(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["email"]
    except jwt.ExpiredSignatureError:
        return None
    except jwt.JWTError:
        return None