from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import AuditMixin


class TaskEvent(AuditMixin, Base):
    __tablename__ = "task_events"

    id: Mapped[int] = mapped_column(primary_key=True)

    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), index=True, nullable=False)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), index=True, nullable=False)

    event_type: Mapped[str] = mapped_column(String(50), index=True, nullable=False)

    actor_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True, nullable=True)

    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)