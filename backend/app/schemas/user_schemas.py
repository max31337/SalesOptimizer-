class UserCreate(BaseModel):
    email: EmailStr
    password: str 
    name: str
    role: str = "sales-rep"