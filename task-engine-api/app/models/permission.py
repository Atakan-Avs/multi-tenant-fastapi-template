from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import AuditMixin


class Permission(AuditMixin, Base):
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # e.g. "task.create"
    description: Mapped[str] = mapped_column(String(255), nullable=False, default="")

    __table_args__ = (
        UniqueConstraint("code", name="uq_permissions_code"),
    )