from sqlalchemy import Table, Column, Integer, ForeignKey, UniqueConstraint
from app.db.base import Base

user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False),
    UniqueConstraint("user_id", "role_id", name="uq_user_roles_user_id_role_id"),
)

role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False),
    Column("permission_id", Integer, ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False),
    UniqueConstraint("role_id", "permission_id", name="uq_role_permissions_role_id_permission_id"),
)