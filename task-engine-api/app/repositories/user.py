from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models import User

def create_user(db: Session, org_id: int, email: str, full_name: str, hashed_password: str) -> User:
    user = User(org_id=org_id, email=email, full_name=full_name, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def list_users_by_org(db: Session, org_id: int) -> list[User]:
    stmt = select(User).where(User.org_id == org_id).order_by(User.id)
    return list(db.execute(stmt).scalars().all())

def get_user_by_email(db: Session, email: str) -> User | None:
    stmt = select(User).where(User.email == email)
    return db.execute(stmt).scalar_one_or_none()


def get_user_by_email_in_org(db: Session, org_id: int, email: str) -> User | None:
    return (
        db.query(User)
        .filter(User.org_id == org_id, User.email == email)
        .first()
    )