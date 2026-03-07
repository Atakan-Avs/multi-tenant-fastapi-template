from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Task, TaskEvent


# ---------- Queries (read) ----------

def get_task(
    db: Session,
    *,
    task_id: int,
    org_id: int,
    include_deleted: bool = False,
) -> Task | None:
    stmt = select(Task).where(Task.id == task_id, Task.org_id == org_id)
    if not include_deleted:
        stmt = stmt.where(Task.deleted_at.is_(None))
    return db.execute(stmt).scalars().first()


def list_tasks(
    db: Session,
    *,
    org_id: int,
    include_deleted: bool = False,
    assigned_to_user_id: int | None = None,
    status: str | None = None,
) -> list[Task]:
    stmt = select(Task).where(Task.org_id == org_id)

    if not include_deleted:
        stmt = stmt.where(Task.deleted_at.is_(None))

    if assigned_to_user_id is not None:
        stmt = stmt.where(Task.assigned_to_user_id == assigned_to_user_id)

    if status is not None:
        stmt = stmt.where(Task.status == status)

    return db.execute(stmt).scalars().all()


# ---------- Commands (write) ----------

def add_task(
    db: Session,
    *,
    org_id: int,
    title: str,
    description: str | None,
    priority: str,
    assigned_to_user_id: int | None,
    due_date,
    actor_user_id: int | None,
) -> Task:
    task = Task(
        org_id=org_id,
        title=title,
        description=description,
        priority=priority,
        assigned_to_user_id=assigned_to_user_id,
        due_date=due_date,
    )

    # audit
    if hasattr(task, "created_by"):
        task.created_by = actor_user_id
    if hasattr(task, "updated_by"):
        task.updated_by = actor_user_id

    db.add(task)
    # id lazım olacak -> flush
    db.flush()
    return task


def apply_task_patch(
    *,
    task: Task,
    patch: dict,
    actor_user_id: int | None,
) -> Task:
    for k, v in patch.items():
        setattr(task, k, v)

    if hasattr(task, "updated_by"):
        task.updated_by = actor_user_id

    return task


def mark_task_deleted(*, task: Task, actor_user_id: int | None) -> Task:
    task.deleted_at = datetime.now(timezone.utc)
    if hasattr(task, "deleted_by"):
        task.deleted_by = actor_user_id
    if hasattr(task, "updated_by"):
        task.updated_by = actor_user_id
    return task


def mark_task_restored(*, task: Task, actor_user_id: int | None) -> Task:
    task.deleted_at = None
    if hasattr(task, "deleted_by"):
        task.deleted_by = None
    if hasattr(task, "updated_by"):
        task.updated_by = actor_user_id
    return task


def add_task_event(
    db: Session,
    *,
    org_id: int,
    task_id: int,
    event_type: str,
    actor_user_id: int | None,
    payload: dict,
) -> TaskEvent:
    evt = TaskEvent(
        org_id=org_id,
        task_id=task_id,
        event_type=event_type,
        actor_user_id=actor_user_id,
        payload=payload,
    )
    db.add(evt)
    return evt