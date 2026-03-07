from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import User
from app.repositories.rbac import (
    create_role,
    get_role_by_id_in_org,
    get_permission_by_code,
    assign_permission_to_role,
    remove_permission_from_role,
    assign_role_to_user,
    remove_role_from_user,
    list_roles_in_org,
    list_permissions,
    list_permissions_for_role,
    list_roles_for_user,
    list_effective_permissions_for_user,
)
from app.models import User as UserModel  # sende model importu böyleyse kalsın, değilse düzelt


def create_role_service(db: Session, *, current_user: User, name: str) -> dict:
    if not name or len(name) < 2:
        raise HTTPException(status_code=400, detail="Invalid role name")

    role = create_role(db, org_id=current_user.org_id, name=name.strip())
    db.commit()
    return {"id": role.id, "org_id": role.org_id, "name": role.name}


def assign_permission_service(db: Session, *, current_user: User, role_id: int, permission_code: str) -> dict:
    role = get_role_by_id_in_org(db, role_id=role_id, org_id=current_user.org_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    perm = get_permission_by_code(db, code=permission_code)
    if not perm:
        raise HTTPException(status_code=404, detail="Permission not found")

    assign_permission_to_role(db, role_id=role.id, permission_id=perm.id)
    db.commit()
    return {"ok": True}


def remove_permission_service(db: Session, *, current_user: User, role_id: int, permission_code: str) -> dict:
    role = get_role_by_id_in_org(db, role_id=role_id, org_id=current_user.org_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    perm = get_permission_by_code(db, code=permission_code)
    if not perm:
        raise HTTPException(status_code=404, detail="Permission not found")

    remove_permission_from_role(db, role_id=role.id, permission_id=perm.id)
    db.commit()
    return {"ok": True}


def assign_role_to_user_service(db: Session, *, current_user: User, target_user_id: int, role_id: int) -> dict:
    role = get_role_by_id_in_org(db, role_id=role_id, org_id=current_user.org_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    target_user = db.get(UserModel, target_user_id)
    if not target_user or getattr(target_user, "deleted_at", None) is not None:
        raise HTTPException(status_code=404, detail="User not found")

    if target_user.org_id != current_user.org_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    assign_role_to_user(db, user_id=target_user.id, role_id=role.id)
    db.commit()
    return {"ok": True}


def remove_role_from_user_service(db: Session, *, current_user: User, target_user_id: int, role_id: int) -> dict:
    role = get_role_by_id_in_org(db, role_id=role_id, org_id=current_user.org_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    target_user = db.get(UserModel, target_user_id)
    if not target_user or getattr(target_user, "deleted_at", None) is not None:
        raise HTTPException(status_code=404, detail="User not found")

    if target_user.org_id != current_user.org_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    remove_role_from_user(db, user_id=target_user.id, role_id=role.id)
    db.commit()
    return {"ok": True}

def list_roles_service(db: Session, *, current_user: User) -> list[dict]:
    roles = list_roles_in_org(db, org_id=current_user.org_id)
    return [{"id": r.id, "org_id": r.org_id, "name": r.name} for r in roles]


def list_permissions_service(db: Session, *, current_user: User) -> list[dict]:
    perms = list_permissions(db)
    out = []
    for p in perms:
        out.append(
            {
                "id": p.id,
                "code": p.code,
                "description": getattr(p, "description", None),
            }
        )
    return out


def list_role_permissions_service(db: Session, *, current_user: User, role_id: int) -> list[dict]:
    role = get_role_by_id_in_org(db, role_id=role_id, org_id=current_user.org_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    perms = list_permissions_for_role(db, role_id=role.id, org_id=current_user.org_id)
    return [{"id": p.id, "code": p.code, "description": getattr(p, "description", None)} for p in perms]


def list_user_roles_service(db: Session, *, current_user: User, target_user_id: int) -> list[dict]:
    target_user = db.get(UserModel, target_user_id)
    if not target_user or getattr(target_user, "deleted_at", None) is not None:
        raise HTTPException(status_code=404, detail="User not found")

    if target_user.org_id != current_user.org_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    roles = list_roles_for_user(db, user_id=target_user.id, org_id=current_user.org_id)
    return [{"id": r.id, "org_id": r.org_id, "name": r.name} for r in roles]


def list_user_permissions_service(db: Session, *, current_user: User, target_user_id: int) -> dict:
    target_user = db.get(UserModel, target_user_id)
    if not target_user or getattr(target_user, "deleted_at", None) is not None:
        raise HTTPException(status_code=404, detail="User not found")

    if target_user.org_id != current_user.org_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    codes = list_effective_permissions_for_user(db, user_id=target_user.id, org_id=current_user.org_id)
    return {"user_id": target_user.id, "permissions": codes}