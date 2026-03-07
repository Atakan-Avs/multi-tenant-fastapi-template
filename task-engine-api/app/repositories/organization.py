from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Organization


def _utcnow():
    return datetime.now(timezone.utc)


def create_org(db: Session, name: str, actor_user_id: int | None = None) -> Organization:
    org = Organization(name=name)

    # audit
    if hasattr(org, "created_by"):
        org.created_by = actor_user_id
    if hasattr(org, "updated_by"):
        org.updated_by = actor_user_id

    db.add(org)
    db.commit()
    db.refresh(org)
    return org


def get_org(db: Session, org_id: int, include_deleted: bool = False) -> Organization | None:
    stmt = select(Organization).where(Organization.id == org_id)

    # default scope: soft deleted gelmesin
    if not include_deleted:
        stmt = stmt.where(Organization.deleted_at.is_(None))

    return db.execute(stmt).scalars().first()


def get_org_by_name(db: Session, name: str, include_deleted: bool = False) -> Organization | None:
    stmt = select(Organization).where(Organization.name == name)

    if not include_deleted:
        stmt = stmt.where(Organization.deleted_at.is_(None))

    return db.execute(stmt).scalars().first()


def soft_delete_org(db: Session, org: Organization, actor_user_id: int | None = None) -> Organization:
    org.deleted_at = _utcnow()

    # audit
    if hasattr(org, "deleted_by"):
        org.deleted_by = actor_user_id

    db.add(org)
    db.commit()
    db.refresh(org)
    return org


def restore_org(db: Session, org: Organization, actor_user_id: int | None = None) -> Organization:
    # admin/owner için
    org.deleted_at = None

    if hasattr(org, "deleted_by"):
        org.deleted_by = None
    if hasattr(org, "updated_by"):
        org.updated_by = actor_user_id

    db.add(org)
    db.commit()
    db.refresh(org)
    return org