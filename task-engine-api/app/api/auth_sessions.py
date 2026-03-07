from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.core.auth import get_current_user
from app.services.auth import revoke_session_service
from app.models import User
from app.repositories.refresh_tokens import list_active_refresh_tokens_for_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/sessions")
def list_sessions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    sessions = list_active_refresh_tokens_for_user(db, user_id=current_user.id)

    # token_hash asla dönmüyoruz
    return {
        "items": [
            {
                "id": s.id,
                "created_at": s.created_at,
                "last_used_at": getattr(s, "last_used_at", None),
                "expires_at": s.expires_at,
                "revoked_at": s.revoked_at,
                "rotated_at": s.rotated_at,
            }
            for s in sessions
        ]
    }
    
@router.delete("/sessions/{session_id}")
def revoke_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return revoke_session_service(
        db,
        current_user_id=current_user.id,
        session_id=session_id,
    )