from fastapi import APIRouter, Depends
from app.core.auth import get_current_user
from app.schemas.user import UserOut
from app.models import User

router = APIRouter(tags=["me"])

@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user