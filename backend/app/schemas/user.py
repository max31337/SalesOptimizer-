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
    confirm_password: str

    @model_validator(mode='after')
    def passwords_match(self) -> 'PasswordUpdate':
        if self.password != self.confirm_password:
            raise ValueError('Passwords do not match')
        return self

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
    username: str
    password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)
    invitation_token: str

    @model_validator(mode='after')
    def passwords_match(self) -> 'InvitedUserCompleteRegistration':
        if self.password != self.confirm_password:
            raise ValueError('Passwords do not match')
        return self

    class Config:
        json_schema_extra = {
            "example": {
                "username": "newuser",
                "password": "securepassword",
                "confirm_password": "securepassword",
                "invitation_token": "jwt.token.here"
            }
        }
