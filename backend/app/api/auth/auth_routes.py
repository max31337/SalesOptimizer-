from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import User
from app.schemas.user import UserCreate
from app.schemas.user import UserLogin
from app.api.auth.auth import verify_password, create_access_token
from app.api.auth.auth import hash_password  

router = APIRouter()

@router.post("/api/auth/register/")
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    hashed_pwd = hash_password(user_data.password)

    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password=hashed_pwd 
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Debugging: Print user data
    # print("📢 New User Created:", new_user.name)

    # Generate JWT token for the new user
    access_token = create_access_token(data={"sub": new_user.email})

    response = {
        "msg": "User created successfully",
        "access_token": access_token,
        "token_type": "bearer",
        "name": new_user.name
    }

    # Debugging: Print response before returning
    # print("📢 API Response:", response)

    return response



@router.post("/api/auth/login/")
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()

    if not user or not verify_password(user_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token({"sub": user.email})

    return {
        "msg": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
        "name": user.name
    }
