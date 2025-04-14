from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models import User, LoginActivity
from app.schemas.user import UserCreate, UserLogin
from app.utils.token import generate_verification_token
from app.core.auth import create_access_token, get_current_user
from app.utils.security import get_password_hash as hash_password, verify_password
from app.services.email import send_verification_email

router = APIRouter()

@router.post("/register/")
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.email == user_data.email) | (User.username == user_data.username)
        ).first()
        if existing_user:
            if existing_user.email == user_data.email:
                raise HTTPException(status_code=400, detail="Email already registered")
            else:
                raise HTTPException(status_code=400, detail="Username already taken")

        verification_token = generate_verification_token()
        hashed_pwd = hash_password(user_data.password)

        new_user = User(
            username=user_data.username,
            name=user_data.name,
            email=user_data.email,
            password=hashed_pwd,
            role=user_data.role,
            is_active=True,
            is_verified=False,
            verification_token=verification_token
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Send verification email
        send_verification_email(new_user.email, verification_token)

        return {
            "msg": "User created successfully. Please check your email to verify your account.",
            "username": new_user.username,
            "name": new_user.name,
            "role": new_user.role,
            "is_verified": new_user.is_verified
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login/")
def login(user_data: UserLogin, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()
    success = False
    
    try:
        if not user or not verify_password(user_data.password, user.password):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        if not user.is_active:
            raise HTTPException(status_code=401, detail="User account is inactive")

        login_activity = LoginActivity(
            user_id=user.id,
            ip_address=request.client.host,
            success=True
        )
        db.add(login_activity)
        db.commit()
        
        access_token = create_access_token({"sub": user.email})
        success = True
        
        return {
            "msg": "Login successful",
            "access_token": access_token,
            "token_type": "bearer",
            "name": user.name,
            "role": user.role,
            "is_active": user.is_active,
            "is_verified": user.is_verified
        }
    finally:
        if not success:
            login_activity = LoginActivity(
                user_id=user.id if user else None,
                ip_address=request.client.host,
                success=False
            )
            db.add(login_activity)
            db.commit()