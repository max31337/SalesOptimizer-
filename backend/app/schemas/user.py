from pydantic import BaseModel, EmailStr
from typing import Literal, Optional

class UserCreate(BaseModel):
    username: str
    name: str
    email: EmailStr
    password: str
    role: Literal["admin", "sales-rep", "analyst"] = "sales-rep"
    invitation_token: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class PasswordReset(BaseModel):
    email: EmailStr

class PasswordUpdate(BaseModel):
    password: str