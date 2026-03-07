from sqlalchemy import String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import AuditMixin


class Role(AuditMixin, Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)  # "admin", "member" etc.

    __table_args__ = (
        UniqueConstraint("org_id", "name", name="uq_roles_org_id_name"),
    )

    # relationships (opsiyonel)
    permissions = relationship("Permission", secondary="role_permissions", lazy="selectin")