from fastapi import APIRouter, Depends, status, Query, HTTPException
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.schemas import UserCreate, UserOut
from app.models import User
from app.repositories import (
    create_user,
    list_users_by_org,
    soft_delete_user,
    restore_user,
)
from app.core.authz import require_roles

router = APIRouter(prefix="/orgs/users", tags=["users"])


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user_in_org(
    payload: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("owner", "admin")),
):
    org_id = current_user.org_id

    from app.core.security import hash_password
    hashed_pw = hash_password(payload.password)

    return create_user(
        db,
        org_id=org_id,
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=hashed_pw,
        actor_user_id=current_user.id,  # audit
    )


@router.get("", response_model=list[UserOut])
def list_users(
    include_deleted: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("owner", "admin")),
):
    org_id = current_user.org_id
    return list_users_by_org(db, org_id, include_deleted=include_deleted)


@router.delete("/{user_id}", response_model=UserOut)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("owner", "admin")),
):
    # sadece kendi org'undan user silebilsin
    user = db.get(User, user_id)
    if not user or user.org_id != current_user.org_id:
        raise HTTPException(status_code=404, detail="User not found")

    if getattr(user, "deleted_at", None) is not None:
        # idempotent: zaten silinmişse aynı kaydı dön
        return user

    return soft_delete_user(db, user, actor_user_id=current_user.id)


@router.post("/{user_id}/restore", response_model=UserOut)
def restore_deleted_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("owner", "admin")),
):
    user = db.get(User, user_id)
    if not user or user.org_id != current_user.org_id:
        raise HTTPException(status_code=404, detail="User not found")

    if getattr(user, "deleted_at", None) is None:
        return user

    return restore_user(db, user, actor_user_id=current_user.id)