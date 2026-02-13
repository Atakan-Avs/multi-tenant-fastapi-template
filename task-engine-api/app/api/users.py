from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.core.auth import get_current_user
from app.schemas import UserCreate, UserOut
from app.models import User
from app.repositories import create_user, list_users_by_org, get_user_by_email
from app.repositories import get_user_by_email_in_org
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/orgs/users", tags=["users"])


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user_in_org(
    payload: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
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
    )



@router.get("", response_model=list[UserOut])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    org_id = current_user.org_id
    return list_users_by_org(db, org_id)