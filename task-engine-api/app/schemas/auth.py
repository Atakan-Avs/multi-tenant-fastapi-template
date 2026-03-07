from pydantic import BaseModel, EmailStr, Field
from pydantic import BaseModel

class RegisterRequest(BaseModel):
    org_id: int
    email: EmailStr
    full_name: str = Field(default="", max_length=120)
    password: str = Field(min_length=6, max_length=72)

class LoginRequest(BaseModel):
    org_id: int
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"