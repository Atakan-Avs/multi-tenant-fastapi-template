from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(default="", max_length=120)
    password: str = Field(min_length=6, max_length=128)

class UserOut(BaseModel):
    id: int
    org_id: int
    email: str
    full_name: str

    class Config:
        from_attributes = True