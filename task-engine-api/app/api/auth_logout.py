from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.services.auth import logout_service, logout_all_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/logout")
def logout(payload: dict, db: Session = Depends(get_db)):
    refresh_token = payload.get("refresh_token")
    return logout_service(db, refresh_token_plain=refresh_token)


@router.post("/logout-all")
def logout_all(payload: dict, db: Session = Depends(get_db)):
    refresh_token = payload.get("refresh_token")
    return logout_all_service(db, refresh_token_plain=refresh_token)