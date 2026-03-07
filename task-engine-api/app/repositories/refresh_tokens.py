from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models import RefreshToken


def add_refresh_token(db: Session, *, user_id: int, token_hash: str, expires_at) -> RefreshToken:
    rt = RefreshToken(user_id=user_id, token_hash=token_hash, expires_at=expires_at)
    db.add(rt)
    db.flush()  # id üret
    return rt


def get_refresh_token_by_hash(db: Session, token_hash: str) -> RefreshToken | None:
    stmt = (
        select(RefreshToken)
        .where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.deleted_at.is_(None),
        )
        .limit(1)
    )
    return db.execute(stmt).scalars().first()


def revoke_refresh_token(db: Session, *, rt: RefreshToken) -> RefreshToken:
    rt.revoked_at = datetime.now(timezone.utc)
    db.add(rt)
    return rt


def rotate_refresh_token(
    db: Session,
    *,
    rt: RefreshToken,
    new_token_hash: str,
    new_expires_at,
) -> RefreshToken:
    now = datetime.now(timezone.utc)
    rt.revoked_at = now
    rt.rotated_at = now
    db.add(rt)

    new_rt = RefreshToken(
        user_id=rt.user_id,
        token_hash=new_token_hash,
        expires_at=new_expires_at,
    )
    db.add(new_rt)
    db.flush()
    return new_rt


def revoke_all_refresh_tokens_for_user(db: Session, *, user_id: int) -> int:
    """Reuse detection için: user'ın tüm aktif refresh tokenlarını revoke et."""
    now = datetime.now(timezone.utc)
    stmt = (
        update(RefreshToken)
        .where(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked_at.is_(None),
            RefreshToken.deleted_at.is_(None),
        )
        .values(revoked_at=now)
    )
    res = db.execute(stmt)
    return res.rowcount or 0

# Backward compatibility: eski kodları kırmamak için
def create_refresh_token(db: Session, user_id: int, token_hash: str, expires_at):
    rt = add_refresh_token(db, user_id=user_id, token_hash=token_hash, expires_at=expires_at)
    db.commit()
    db.refresh(rt)
    return rt


def touch_refresh_token_last_used(db: Session, *, rt: RefreshToken) -> RefreshToken:
    rt.last_used_at = datetime.now(timezone.utc)
    db.add(rt)
    return rt


def list_active_refresh_tokens_for_user(db: Session, *, user_id: int) -> list[RefreshToken]:
    """
    Session listesi için: revoked olmayan ve soft-delete olmayan tokenlar.
    """
    stmt = (
        select(RefreshToken)
        .where(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked_at.is_(None),
            RefreshToken.deleted_at.is_(None),
        )
        .order_by(RefreshToken.created_at.desc())
    )
    return list(db.execute(stmt).scalars().all())

def revoke_refresh_token_by_id(
    db: Session,
    *,
    session_id: int,
    user_id: int,
) -> RefreshToken | None:
    """
    Sadece o user'a ait session revoke edilir.
    Başka user'ın session'ına dokunulamaz.
    """
    stmt = (
        select(RefreshToken)
        .where(
            RefreshToken.id == session_id,
            RefreshToken.user_id == user_id,
            RefreshToken.deleted_at.is_(None),
        )
        .limit(1)
    )

    rt = db.execute(stmt).scalars().first()
    if not rt:
        return None

    if rt.revoked_at is None:
        rt.revoked_at = datetime.now(timezone.utc)
        db.add(rt)

    return rt