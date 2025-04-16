from pydantic import BaseModel

class UserResponse(BaseModel):
    msg: str
    username: str
    name: str
    role: str
    is_verified: bool