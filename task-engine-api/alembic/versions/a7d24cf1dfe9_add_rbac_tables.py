"""add rbac tables

Revision ID: a7d24cf1dfe9
Revises: bd587df45630
Create Date: 2026-02-24 19:58:18.513750

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a7d24cf1dfe9'
down_revision: Union[str, Sequence[str], None] = 'bd587df45630'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "permissions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("code", name="uq_permissions_code"),
    )
    op.create_index("ix_permissions_code", "permissions", ["code"])

    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("org_id", sa.Integer(), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("org_id", "name", name="uq_roles_org_id_name"),
    )
    op.create_index("ix_roles_org_id", "roles", ["org_id"])

    op.create_table(
        "user_roles",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role_id", sa.Integer(), sa.ForeignKey("roles.id", ondelete="CASCADE"), nullable=False),
        sa.UniqueConstraint("user_id", "role_id", name="uq_user_roles_user_id_role_id"),
    )

    op.create_table(
        "role_permissions",
        sa.Column("role_id", sa.Integer(), sa.ForeignKey("roles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("permission_id", sa.Integer(), sa.ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False),
        sa.UniqueConstraint("role_id", "permission_id", name="uq_role_permissions_role_id_permission_id"),
    )

    # seed permissions
    op.execute("""
        INSERT INTO permissions (code, description, created_at)
        VALUES
          ('task.read',   'Read tasks',   NOW()),
          ('task.create', 'Create tasks', NOW()),
          ('task.update', 'Update tasks', NOW()),
          ('task.delete', 'Delete tasks', NOW())
        ON CONFLICT (code) DO NOTHING;
    """)

    # seed roles per org
    op.execute("""
        INSERT INTO roles (org_id, name, created_at)
        SELECT o.id, 'admin', NOW()
        FROM organizations o
        WHERE NOT EXISTS (
            SELECT 1 FROM roles r WHERE r.org_id = o.id AND r.name = 'admin'
        );
    """)
    op.execute("""
        INSERT INTO roles (org_id, name, created_at)
        SELECT o.id, 'member', NOW()
        FROM organizations o
        WHERE NOT EXISTS (
            SELECT 1 FROM roles r WHERE r.org_id = o.id AND r.name = 'member'
        );
    """)

    # admin -> all permissions
    op.execute("""
        INSERT INTO role_permissions (role_id, permission_id)
        SELECT r.id, p.id
        FROM roles r
        JOIN permissions p ON 1=1
        WHERE r.name = 'admin'
        ON CONFLICT DO NOTHING;
    """)

    # member -> task.read only
    op.execute("""
        INSERT INTO role_permissions (role_id, permission_id)
        SELECT r.id, p.id
        FROM roles r
        JOIN permissions p ON p.code = 'task.read'
        WHERE r.name = 'member'
        ON CONFLICT DO NOTHING;
    """)

    # backfill users.role -> user_roles
    op.execute("""
        INSERT INTO user_roles (user_id, role_id)
        SELECT u.id, r.id
        FROM users u
        JOIN roles r ON r.org_id = u.org_id AND r.name = 'admin'
        WHERE u.role = 'admin'
        ON CONFLICT DO NOTHING;
    """)
    op.execute("""
        INSERT INTO user_roles (user_id, role_id)
        SELECT u.id, r.id
        FROM users u
        JOIN roles r ON r.org_id = u.org_id AND r.name = 'member'
        WHERE u.role IS NULL OR u.role <> 'admin'
        ON CONFLICT DO NOTHING;
    """)


def downgrade() -> None:
    op.drop_table("role_permissions")
    op.drop_table("user_roles")
    op.drop_index("ix_roles_org_id", table_name="roles")
    op.drop_table("roles")
    op.drop_index("ix_permissions_code", table_name="permissions")
    op.drop_table("permissions")