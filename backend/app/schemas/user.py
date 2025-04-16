from pydantic import BaseModel, EmailStr, Field, validator, model_validator
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    name: str

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)
    invitation_token: Optional[str] = None

    @validator('confirm_password') # This validator should now be recognized
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
    role: str = Field(default="sales-rep")

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool

class PasswordReset(BaseModel):
    email: EmailStr

class PasswordUpdate(BaseModel):
    password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    email: str
    password: str

class AdminInviteCreate(BaseModel):
    email: EmailStr
    name: str
    role: str = "sales-rep"

    @property
    def username(self) -> str:
        # Generate username from email (part before @)
        return self.email.split('@')[0]

# Add this new schema specifically for invited user registration completion
class InvitedUserCompleteRegistration(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)
    invitation_token: str # Token is required for this step

    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
