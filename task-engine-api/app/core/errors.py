from pydantic import BaseModel

class ApiError(BaseModel):
    code: str
    message: str

class ApiErrorResponse(BaseModel):
    error: ApiError