from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.deps import get_db
from app.schemas import RegisterRequest, LoginRequest, TokenResponse
from app.repositories import (
    get_org,
    get_user_by_email,
    get_user_by_email_in_org,
    create_user,
)
from app.core.security import hash_password, verify_password, create_access_token
from app.core.tokens import generate_refresh_token, hash_token, refresh_expires_at
from app.core.security import create_access_token
from app.repositories.refresh_tokens import add_refresh_token


router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    org = get_org(db, payload.org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    existing = get_user_by_email(db, payload.email)
    if existing:
        raise HTTPException(status_code=409, detail="Email already exists")

    try:
        user = create_user(
            db,
            org_id=payload.org_id,
            email=payload.email,
            full_name=payload.full_name,
            hashed_password=hash_password(payload.password),
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email already exists")

    return {
        "id": user.id,
        "org_id": user.org_id,
        "email": user.email,
        "full_name": user.full_name,
    }

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = get_user_by_email_in_org(db, payload.org_id, payload.email)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(subject=str(user.id))

    # refresh token üret
    plain_refresh = generate_refresh_token()
    token_hash = hash_token(plain_refresh)

    # DB’ye yaz (repo sadece add + flush)
    with db.begin_nested():
        add_refresh_token(
            db,
            user_id=user.id,
            token_hash=token_hash,
            expires_at=refresh_expires_at(),
        )
    db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=plain_refresh,
        token_type="bearer",
    )