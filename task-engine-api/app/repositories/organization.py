from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models import Organization

def create_org(db: Session, name: str) -> Organization:
    org = Organization(name=name)
    db.add(org)
    db.commit()
    db.refresh(org)
    return org

def get_org(db: Session, org_id: int) -> Organization | None:
    return db.get(Organization, org_id)

def get_org_by_name(db: Session, name: str) -> Organization | None:
    stmt = select(Organization).where(Organization.name == name)
    return db.execute(stmt).scalar_one_or_none()