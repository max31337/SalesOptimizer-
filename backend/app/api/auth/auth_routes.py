from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import User
from app.schemas.user import UserCreate
from app.schemas.user import UserLogin
from app.api.auth.auth import verify_password, create_access_token
from app.api.auth.auth import hash_password  
from app.crud.user import verify_user_email
from app.utils.token import generate_verification_token
from app.services.email import send_verification_email
from pydantic import BaseModel
from app.api.auth.auth import get_current_user

router = APIRouter()

@router.post("/auth/register/")
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


@router.post("/auth/login/")  # Remove the /api prefix
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()

    if not user or not verify_password(user_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(status_code=401, detail="User account is inactive")

    access_token = create_access_token({"sub": user.email})

    return {
        "msg": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
        "name": user.name,
        "role": user.role,
        "is_active": user.is_active,
        "is_verified": user.is_verified
    }


@router.get("/auth/verify/{token}")  # Remove the /api prefix
def verify_email(token: str, db: Session = Depends(get_db)):
    """Verify user email with token."""
    try:
        user = verify_user_email(db, token)
        return {"message": "Email verified successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Error verifying email"
        )
class CompleteRegistrationRequest(BaseModel):
    token: str
    username: str
    password: str

@router.post("/auth/complete-registration")
def complete_registration(
    registration_data: CompleteRegistrationRequest,
    db: Session = Depends(get_db)
):
    # Find the user with the invitation token
    user = db.query(User).filter(User.invitation_token == registration_data.token).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Invalid invitation token")
    
    if user.is_active:
        raise HTTPException(status_code=400, detail="Registration already completed")
    
    user.username = registration_data.username  
    user.password = hash_password(registration_data.password)
    user.is_active = True
    user.invitation_token = None  
    
    try:
        db.commit()
        
        access_token = create_access_token(data={"sub": user.email})
        
        return {
            "message": "Registration completed successfully",
            "access_token": access_token,
            "token_type": "bearer"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
