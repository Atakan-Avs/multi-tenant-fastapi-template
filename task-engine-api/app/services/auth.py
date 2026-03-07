from __future__ import annotations

import logging
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.repositories.refresh_tokens import revoke_refresh_token_by_id

from app.core.tokens import hash_token, generate_refresh_token, refresh_expires_at
from app.core.security import create_access_token
from app.models import User
from app.repositories.refresh_tokens import (
    get_refresh_token_by_hash,
    rotate_refresh_token,
    revoke_refresh_token,
    revoke_all_refresh_tokens_for_user,
    touch_refresh_token_last_used,
)

logger = logging.getLogger("app")


def refresh_tokens_service(
    db: Session,
    *,
    refresh_token_plain: str,
    request_id: str | None = None,
    client_ip: str | None = None,
    user_agent: str | None = None,
) -> dict:
    if not refresh_token_plain:
        raise HTTPException(status_code=400, detail="refresh_token is required")

    rt_hash = hash_token(refresh_token_plain)

    rt = get_refresh_token_by_hash(db, rt_hash)
    if not rt:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    # REUSE DETECTION:
    if rt.revoked_at is not None:
        logger.warning(
            "refresh_token_reuse_detected",
            extra={
                "request_id": request_id,
                "user_id": rt.user_id,
                "client_ip": client_ip,
                "user_agent": user_agent,
            },
        )

        with db.begin_nested():
            revoke_all_refresh_tokens_for_user(db, user_id=rt.user_id)
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    # Expired?
    if rt.expires_at <= datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired",
        )

    user = db.get(User, rt.user_id)
    if not user or getattr(user, "deleted_at", None) is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    # ROTATION (atomic)
    new_plain = generate_refresh_token()
    new_hash = hash_token(new_plain)

    with db.begin_nested():
        # session activity
        touch_refresh_token_last_used(db, rt=rt)

        rotate_refresh_token(
            db,
            rt=rt,
            new_token_hash=new_hash,
            new_expires_at=refresh_expires_at(),
        )

    db.commit()

    new_access = create_access_token(subject=str(user.id))
    return {
        "access_token": new_access,
        "refresh_token": new_plain,
        "token_type": "bearer",
    }


def logout_service(
    db: Session,
    *,
    refresh_token_plain: str,
) -> dict:
    """
    Current session logout (idempotent):
    refresh token varsa revoke eder, yoksa da ok döner.
    """
    if not refresh_token_plain:
        raise HTTPException(status_code=400, detail="refresh_token is required")

    rt = get_refresh_token_by_hash(db, hash_token(refresh_token_plain))
    if not rt:
        return {"ok": True}  # idempotent

    if rt.revoked_at is not None:
        return {"ok": True}  # idempotent

    with db.begin_nested():
        revoke_refresh_token(db, rt=rt)
    db.commit()

    return {"ok": True}


def logout_all_service(
    db: Session,
    *,
    refresh_token_plain: str,
) -> dict:
    """
    All sessions logout (idempotent):
    verilen refresh token'dan user_id bulur ve o user'ın tüm aktif refresh tokenlarını revoke eder.
    """
    if not refresh_token_plain:
        raise HTTPException(status_code=400, detail="refresh_token is required")

    rt = get_refresh_token_by_hash(db, hash_token(refresh_token_plain))
    if not rt:
        return {"ok": True}  # idempotent

    with db.begin_nested():
        revoke_all_refresh_tokens_for_user(db, user_id=rt.user_id)
    db.commit()

    return {"ok": True}

def revoke_session_service(
    db: Session,
    *,
    current_user_id: int,
    session_id: int,
) -> dict:
    """
    Tek session revoke (device logout)
    """

    rt = revoke_refresh_token_by_id(
        db,
        session_id=session_id,
        user_id=current_user_id,
    )

    if not rt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    db.commit()

    return {"ok": True}