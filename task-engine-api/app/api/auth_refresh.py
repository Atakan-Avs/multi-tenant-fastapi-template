from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.services.auth import refresh_tokens_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/refresh")
def refresh_token(payload: dict, request: Request, db: Session = Depends(get_db)):
    refresh_token_plain = payload.get("refresh_token")

    return refresh_tokens_service(
        db,
        refresh_token_plain=refresh_token_plain,
        request_id=getattr(request.state, "request_id", None),
        client_ip=getattr(request.state, "client_ip", None),
        user_agent=getattr(request.state, "user_agent", None),
    )