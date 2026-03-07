from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User


def _utcnow():
    return datetime.now(timezone.utc)


def create_user(
    db: Session,
    org_id: int,
    email: str,
    full_name: str,
    hashed_password: str,
    actor_user_id: int | None = None,
) -> User:
    user = User(
        org_id=org_id,
        email=email,
        full_name=full_name,
        hashed_password=hashed_password,
    )

    # audit
    if hasattr(user, "created_by"):
        user.created_by = actor_user_id
    if hasattr(user, "updated_by"):
        user.updated_by = actor_user_id

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def list_users_by_org(db: Session, org_id: int, include_deleted: bool = False):
    stmt = select(User).where(User.org_id == org_id)

    # default scope: soft deleted gelmesin
    if not include_deleted:
        stmt = stmt.where(User.deleted_at.is_(None))

    return db.execute(stmt).scalars().all()


def get_user_by_email(db: Session, email: str, include_deleted: bool = False):
    stmt = select(User).where(User.email == email)

    if not include_deleted:
        stmt = stmt.where(User.deleted_at.is_(None))

    return db.execute(stmt).scalars().first()


def get_user_by_email_in_org(
    db: Session,
    org_id: int,
    email: str,
    include_deleted: bool = False,
):
    stmt = select(User).where(User.org_id == org_id, User.email == email)

    if not include_deleted:
        stmt = stmt.where(User.deleted_at.is_(None))

    return db.execute(stmt).scalars().first()


def soft_delete_user(db: Session, user: User, actor_user_id: int | None = None):
    user.deleted_at = _utcnow()

    # audit
    if hasattr(user, "deleted_by"):
        user.deleted_by = actor_user_id

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def restore_user(db: Session, user: User, actor_user_id: int | None = None):
    # admin/owner için
    user.deleted_at = None

    if hasattr(user, "deleted_by"):
        user.deleted_by = None
    if hasattr(user, "updated_by"):
        user.updated_by = actor_user_id

    db.add(user)
    db.commit()
    db.refresh(user)
    return user