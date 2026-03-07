from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import User
from app.repositories.task import (
    add_task,
    add_task_event,
    apply_task_patch,
    get_task,
    list_tasks,
    mark_task_deleted,
    mark_task_restored,
)


def _is_admin_or_owner(user: User) -> bool:
    return user.role in ("owner", "admin")


def create_task_service(
    db: Session,
    *,
    current_user: User,
    title: str,
    description: str | None,
    priority: str,
    assigned_to_user_id: int | None,
    due_date,
):
    with db.begin_nested():
        task = add_task(
            db,
            org_id=current_user.org_id,
            title=title,
            description=description,
            priority=priority,
            assigned_to_user_id=assigned_to_user_id,
            due_date=due_date,
            actor_user_id=current_user.id,
        )
        add_task_event(
            db,
            org_id=current_user.org_id,
            task_id=task.id,
            event_type="task_created",
            actor_user_id=current_user.id,
            payload={
                "title": title,
                "assigned_to_user_id": assigned_to_user_id,
                "priority": priority,
            },
        )

    db.refresh(task)
    return task


def list_tasks_service(
    db: Session,
    *,
    current_user: User,
    include_deleted: bool,
    assigned_to_user_id: int | None,
    status: str | None,
):
    if include_deleted and not _is_admin_or_owner(current_user):
        raise HTTPException(status_code=403, detail="Forbidden")

    if current_user.role == "member":
        assigned_to_user_id = current_user.id

    return list_tasks(
        db,
        org_id=current_user.org_id,
        include_deleted=include_deleted,
        assigned_to_user_id=assigned_to_user_id,
        status=status,
    )


def get_task_service(
    db: Session,
    *,
    current_user: User,
    task_id: int,
    include_deleted: bool,
):
    if include_deleted and not _is_admin_or_owner(current_user):
        raise HTTPException(status_code=403, detail="Forbidden")

    task = get_task(db, task_id=task_id, org_id=current_user.org_id, include_deleted=include_deleted)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if current_user.role == "member" and task.assigned_to_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    return task


def update_task_service(
    db: Session,
    *,
    current_user: User,
    task_id: int,
    patch: dict,
):
    task = get_task(db, task_id=task_id, org_id=current_user.org_id, include_deleted=True)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.deleted_at is not None and not _is_admin_or_owner(current_user):
        raise HTTPException(status_code=403, detail="Forbidden")

    if current_user.role == "member" and task.assigned_to_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    with db.begin_nested():
        apply_task_patch(task=task, patch=patch, actor_user_id=current_user.id)
        add_task_event(
            db,
            org_id=task.org_id,
            task_id=task.id,
            event_type="task_updated",
            actor_user_id=current_user.id,
            payload=patch,
        )

    db.refresh(task)
    return task


def soft_delete_task_service(
    db: Session,
    *,
    current_user: User,
    task_id: int,
):
    task = get_task(db, task_id=task_id, org_id=current_user.org_id, include_deleted=True)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.deleted_at is not None:
        return task

    with db.begin_nested():
        mark_task_deleted(task=task, actor_user_id=current_user.id)
        add_task_event(
            db,
            org_id=task.org_id,
            task_id=task.id,
            event_type="task_deleted",
            actor_user_id=current_user.id,
            payload={},
        )

    db.refresh(task)
    return task


def restore_task_service(
    db: Session,
    *,
    current_user: User,
    task_id: int,
):
    task = get_task(db, task_id=task_id, org_id=current_user.org_id, include_deleted=True)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.deleted_at is None:
        return task

    with db.begin_nested():
        mark_task_restored(task=task, actor_user_id=current_user.id)
        add_task_event(
            db,
            org_id=task.org_id,
            task_id=task.id,
            event_type="task_restored",
            actor_user_id=current_user.id,
            payload={},
        )

    db.refresh(task)
    return task