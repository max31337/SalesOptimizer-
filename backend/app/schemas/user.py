
from pydantic import BaseModel, EmailStr
from typing import Literal, Optional

class UserBase(BaseModel):
    username: str
    name: str
    email: EmailStr
    role: Literal["admin", "sales-rep", "analyst"] = "sales-rep"

class UserCreate(UserBase):
    password: str
    invitation_token: Optional[str] = None

class UserUpdate(BaseModel):
    username: Optional[str] = None
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[Literal["admin", "sales-rep", "analyst"]] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None

class UserLogin(BaseModel):
    email: str
    password: str

class PasswordReset(BaseModel):
    email: EmailStr

class PasswordUpdate(BaseModel):
    password: str

# Add this new schema class
class InviteUser(BaseModel):
    email: EmailStr
    name: str
    role: Literal["admin", "sales-rep", "analyst"]
    username: str  # Added username field
