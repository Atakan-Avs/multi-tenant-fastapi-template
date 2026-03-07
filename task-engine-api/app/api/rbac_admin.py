from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.rbac import require_permission
from app.db.deps import get_db
from app.models import User
from app.services.rbac import (
    create_role_service,
    assign_permission_service,
    remove_permission_service,
    assign_role_to_user_service,
    remove_role_from_user_service,
    # READ services 
    list_roles_service,
    list_permissions_service,
    list_role_permissions_service,
    list_user_roles_service,
    list_user_permissions_service,
)

router = APIRouter(prefix="/rbac", tags=["rbac"])


# -------------------------
# WRITE endpoints 
# -------------------------

@router.post(
    "/roles",
    dependencies=[Depends(require_permission("rbac.manage"))],
)
def create_role(payload: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    name = payload.get("name")
    return create_role_service(db, current_user=current_user, name=name)


@router.post(
    "/roles/{role_id}/permissions",
    dependencies=[Depends(require_permission("rbac.manage"))],
)
def add_permission(role_id: int, payload: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    code = payload.get("code")
    return assign_permission_service(db, current_user=current_user, role_id=role_id, permission_code=code)


@router.delete(
    "/roles/{role_id}/permissions/{code}",
    dependencies=[Depends(require_permission("rbac.manage"))],
)
def remove_permission(role_id: int, code: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return remove_permission_service(db, current_user=current_user, role_id=role_id, permission_code=code)


@router.post(
    "/users/{user_id}/roles/{role_id}",
    dependencies=[Depends(require_permission("rbac.manage"))],
)
def assign_role(user_id: int, role_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return assign_role_to_user_service(db, current_user=current_user, target_user_id=user_id, role_id=role_id)


@router.delete(
    "/users/{user_id}/roles/{role_id}",
    dependencies=[Depends(require_permission("rbac.manage"))],
)
def remove_role(user_id: int, role_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return remove_role_from_user_service(db, current_user=current_user, target_user_id=user_id, role_id=role_id)


# -------------------------
# READ endpoints 
# -------------------------

@router.get(
    "/roles",
    dependencies=[Depends(require_permission("rbac.manage"))],
)
def list_roles(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Org içindeki tüm roller (admin panel için).
    """
    return list_roles_service(db, current_user=current_user)


@router.get(
    "/permissions",
    dependencies=[Depends(require_permission("rbac.manage"))],
)
def list_permissions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Sistemdeki tüm permission'lar.
    """
    return list_permissions_service(db, current_user=current_user)


@router.get(
    "/roles/{role_id}/permissions",
    dependencies=[Depends(require_permission("rbac.manage"))],
)
def list_role_permissions(role_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Role'a bağlı permission listesi.
    """
    return list_role_permissions_service(db, current_user=current_user, role_id=role_id)


@router.get(
    "/users/{user_id}/roles",
    dependencies=[Depends(require_permission("rbac.manage"))],
)
def list_user_roles(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    User'ın role listesi (admin panel / debug).
    """
    return list_user_roles_service(db, current_user=current_user, target_user_id=user_id)


@router.get(
    "/users/{user_id}/permissions",
    dependencies=[Depends(require_permission("rbac.manage"))],
)
def list_user_permissions(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    User'ın effective permission listesi (role->permission flatten).
    """
    return list_user_permissions_service(db, current_user=current_user, target_user_id=user_id)