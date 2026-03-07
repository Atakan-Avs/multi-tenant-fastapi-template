from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.core.auth import get_current_user
from app.core.rbac import require_permission
from app.models import User
from app.schemas.task import TaskCreate, TaskUpdate, TaskOut
from app.services import (
    create_task_service,
    list_tasks_service,
    get_task_service,
    update_task_service,
    soft_delete_task_service,
    restore_task_service,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post(
    "",
    response_model=TaskOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("task.create"))],
)
def create_task_endpoint(
    payload: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_task_service(
        db,
        current_user=current_user,
        title=payload.title,
        description=payload.description,
        priority=payload.priority,
        assigned_to_user_id=payload.assigned_to_user_id,
        due_date=payload.due_date,
    )


@router.get(
    "",
    response_model=list[TaskOut],
    dependencies=[Depends(require_permission("task.read"))],
)
def list_tasks_endpoint(
    include_deleted: bool = Query(False),
    assigned_to_user_id: int | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_tasks_service(
        db,
        current_user=current_user,
        include_deleted=include_deleted,
        assigned_to_user_id=assigned_to_user_id,
        status=status_filter,
    )


@router.get(
    "/{task_id}",
    response_model=TaskOut,
    dependencies=[Depends(require_permission("task.read"))],
)
def get_task_endpoint(
    task_id: int,
    include_deleted: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_task_service(
        db,
        current_user=current_user,
        task_id=task_id,
        include_deleted=include_deleted,
    )


@router.patch(
    "/{task_id}",
    response_model=TaskOut,
    dependencies=[Depends(require_permission("task.update"))],
)
def update_task_endpoint(
    task_id: int,
    payload: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    patch = payload.model_dump(exclude_unset=True)
    return update_task_service(
        db,
        current_user=current_user,
        task_id=task_id,
        patch=patch,
    )


@router.delete(
    "/{task_id}",
    response_model=TaskOut,
    dependencies=[Depends(require_permission("task.delete"))],
)
def delete_task_endpoint(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return soft_delete_task_service(
        db,
        current_user=current_user,
        task_id=task_id,
    )


@router.post(
    "/{task_id}/restore",
    response_model=TaskOut,
    dependencies=[Depends(require_permission("task.delete"))],
)
def restore_task_endpoint(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return restore_task_service(
        db,
        current_user=current_user,
        task_id=task_id,
    )