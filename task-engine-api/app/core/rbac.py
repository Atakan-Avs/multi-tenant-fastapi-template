from __future__ import annotations

from enum import Enum

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.core.auth import get_current_user
from app.models import User
from app.models.permission import Permission
from app.models.role import Role
from app.models.rbac_links import user_roles, role_permissions


class UserRole(str, Enum):
    owner = "owner"
    admin = "admin"
    member = "member"


def _get_user_permission_codes(db: Session, *, user_id: int) -> set[str]:
    stmt = (
        select(Permission.code)
        .select_from(Permission)
        .join(role_permissions, role_permissions.c.permission_id == Permission.id)
        .join(Role, Role.id == role_permissions.c.role_id)
        .join(user_roles, user_roles.c.role_id == Role.id)
        .where(user_roles.c.user_id == user_id)
        .where(Permission.deleted_at.is_(None))
        .where(Role.deleted_at.is_(None))
    )
    rows = db.execute(stmt).all()
    return {r[0] for r in rows}


def require_permission(code: str):
    """
    Usage:
      dependencies=[Depends(require_permission("task.create"))]
    """

    def _dep(
        request: Request,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        cached = getattr(request.state, "perm_codes", None)
        if cached is None:
            cached = _get_user_permission_codes(db, user_id=current_user.id)
            request.state.perm_codes = cached

        if code not in cached:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden",
            )
        return True

    return _dep