import os
import jwt
from datetime import datetime, timedelta
from jose import JWTError, jwt
from dotenv import load_dotenv
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import User
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer


load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash the password before storing in the database."""
    return pwd_context.hash(password)

def authenticate_user(email: str, password: str, db: Session):
    """Authenticate user using SQLAlchemy with email instead of username."""
    user = db.query(User).filter(User.email == email).first()
    
    if not user or not pwd_context.verify(password, user.hashed_password):
        return None 
    
    return user  

def create_jwt_token(email: str):
    """Generate a JWT token for the given email."""
    token = jwt.encode(
        {"sub": email, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)},
        SECRET_KEY,
        algorithm="HS256"
    )
    return token


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Add this near the top with other constants
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

# Add this new function
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get current user from JWT token."""
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user