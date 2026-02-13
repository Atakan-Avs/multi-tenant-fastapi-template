from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.schemas import OrganizationCreate, OrganizationOut
from app.repositories import create_org, get_org_by_name

router = APIRouter(prefix="/orgs", tags=["orgs"])

@router.post("", response_model=OrganizationOut, status_code=status.HTTP_201_CREATED)
def create_organization(payload: OrganizationCreate, db: Session = Depends(get_db)):
    existing = get_org_by_name(db, payload.name)
    if existing:
        raise HTTPException(status_code=409, detail="Organization name already exists")
    return create_org(db, payload.name)