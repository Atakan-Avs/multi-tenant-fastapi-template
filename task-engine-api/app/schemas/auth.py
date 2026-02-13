from pydantic import BaseModel, EmailStr, Field

class RegisterRequest(BaseModel):
    org_id: int
    email: EmailStr
    full_name: str = Field(default="", max_length=120)
    password: str = Field(min_length=6, max_length=72)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=72)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"