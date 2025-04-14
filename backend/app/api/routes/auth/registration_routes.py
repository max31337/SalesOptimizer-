from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.user import UserCreate
from app.crud.user_repository import UserRepository  # Updated import
from app.utils.security import create_verification_token
from app.utils.email import send_verification_email
from app.models import User

router = APIRouter()

@router.post("/auth/register/")
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    user_service = UserService()
    return await user_service.create_user(user_data)