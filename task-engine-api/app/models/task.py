from __future__ import annotations

from enum import Enum
from datetime import datetime

from sqlalchemy import ForeignKey, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import AuditMixin


class TaskStatus(str, Enum):
    todo = "todo"
    doing = "doing"
    done = "done"


class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Task(AuditMixin, Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)

    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), index=True, nullable=False)

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[str] = mapped_column(String(20), nullable=False, default=TaskStatus.todo.value)
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default=TaskPriority.medium.value)

    assigned_to_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True, nullable=True)

    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)