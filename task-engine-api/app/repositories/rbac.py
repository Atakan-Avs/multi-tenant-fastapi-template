from __future__ import annotations

from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.models.role import Role
from app.models.permission import Permission
from app.models.rbac_links import user_roles, role_permissions
from app.models.user import User 
from sqlalchemy import distinct  


def get_role_by_id_in_org(db: Session, *, role_id: int, org_id: int) -> Role | None:
    stmt = (
        select(Role)
        .where(Role.id == role_id, Role.org_id == org_id, Role.deleted_at.is_(None))
        .limit(1)
    )
    return db.execute(stmt).scalars().first()


def get_permission_by_code(db: Session, *, code: str) -> Permission | None:
    stmt = select(Permission).where(Permission.code == code, Permission.deleted_at.is_(None)).limit(1)
    return db.execute(stmt).scalars().first()


def create_role(db: Session, *, org_id: int, name: str) -> Role:
    role = Role(org_id=org_id, name=name)
    db.add(role)
    db.flush()
    return role


def assign_permission_to_role(db: Session, *, role_id: int, permission_id: int) -> None:
    stmt = (
        pg_insert(role_permissions)
        .values(role_id=role_id, permission_id=permission_id)
        .on_conflict_do_nothing(index_elements=["role_id", "permission_id"])
    )
    db.execute(stmt)


def remove_permission_from_role(db: Session, *, role_id: int, permission_id: int) -> int:
    res = db.execute(
        delete(role_permissions).where(
            role_permissions.c.role_id == role_id,
            role_permissions.c.permission_id == permission_id,
        )
    )
    return res.rowcount or 0


def assign_role_to_user(db: Session, *, user_id: int, role_id: int) -> None:
    stmt = (
        pg_insert(user_roles)
        .values(user_id=user_id, role_id=role_id)
        .on_conflict_do_nothing(index_elements=["user_id", "role_id"])
    )
    db.execute(stmt)


def remove_role_from_user(db: Session, *, user_id: int, role_id: int) -> int:
    res = db.execute(
        delete(user_roles).where(
            user_roles.c.user_id == user_id,
            user_roles.c.role_id == role_id,
        )
    )
    return res.rowcount or 0


def list_roles_in_org(db: Session, *, org_id: int) -> list[Role]:
    stmt = (
        select(Role)
        .where(Role.org_id == org_id, Role.deleted_at.is_(None))
        .order_by(Role.id.asc())
    )
    return list(db.execute(stmt).scalars().all())


def list_permissions(db: Session) -> list[Permission]:
    stmt = (
        select(Permission)
        .where(Permission.deleted_at.is_(None))
        .order_by(Permission.code.asc())
    )
    return list(db.execute(stmt).scalars().all())


def list_permissions_for_role(db: Session, *, role_id: int, org_id: int) -> list[Permission]:
    # org guard: role org_id kontrolü join ile
    stmt = (
        select(Permission)
        .join(role_permissions, role_permissions.c.permission_id == Permission.id)
        .join(Role, Role.id == role_permissions.c.role_id)
        .where(
            Role.id == role_id,
            Role.org_id == org_id,
            Role.deleted_at.is_(None),
            Permission.deleted_at.is_(None),
        )
        .order_by(Permission.code.asc())
    )
    return list(db.execute(stmt).scalars().all())


def list_roles_for_user(db: Session, *, user_id: int, org_id: int) -> list[Role]:
    stmt = (
        select(Role)
        .select_from(User)
        .join(user_roles, user_roles.c.user_id == User.id)
        .join(Role, Role.id == user_roles.c.role_id)
        .where(
            User.id == user_id,
            User.org_id == org_id,
            User.deleted_at.is_(None),
            Role.org_id == org_id,
            Role.deleted_at.is_(None),
        )
        .order_by(Role.id.asc())
    )
    return list(db.execute(stmt).scalars().all())


def list_effective_permissions_for_user(db: Session, *, user_id: int, org_id: int) -> list[str]:
    # user -> user_roles -> roles -> role_permissions -> permissions
    stmt = (
        select(distinct(Permission.code))
        .select_from(User)
        .join(user_roles, user_roles.c.user_id == User.id)
        .join(Role, Role.id == user_roles.c.role_id)
        .join(role_permissions, role_permissions.c.role_id == Role.id)
        .join(Permission, Permission.id == role_permissions.c.permission_id)
        .where(
            User.id == user_id,
            User.org_id == org_id,
            User.deleted_at.is_(None),
            Role.org_id == org_id,
            Role.deleted_at.is_(None),
            Permission.deleted_at.is_(None),
        )
        .order_by(Permission.code.asc())
    )
    rows = db.execute(stmt).all()
    return [r[0] for r in rows]