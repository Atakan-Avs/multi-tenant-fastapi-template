from fastapi import Depends, HTTPException, status
from app.core.auth import get_current_user
from app.models import User


def require_roles(*allowed_roles: str):
    def _dep(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden",
            )
        return current_user

    return _dep