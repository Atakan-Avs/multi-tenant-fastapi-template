from sqlalchemy import Column, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import AuditMixin
from app.models.rbac_links import user_roles


class User(AuditMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), index=True)

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(120), default="")
    hashed_password: Mapped[str] = mapped_column(String(255))
    role = Column(String(20), nullable=False, default="member")

    organization = relationship("Organization")
    roles = relationship("Role", secondary=user_roles, lazy="selectin")

    __table_args__ = (
        UniqueConstraint("org_id", "email", name="uq_users_org_id_email"),
    )