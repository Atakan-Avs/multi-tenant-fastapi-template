"""add audit_by fields to rbac tables

Revision ID: 98f68d1d9cdf
Revises: 2c3b02673b7a
Create Date: 2026-02-24 21:41:37.029651

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '98f68d1d9cdf'
down_revision: Union[str, Sequence[str], None] = '2c3b02673b7a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # roles
    op.add_column("roles", sa.Column("created_by", sa.Integer(), nullable=True))
    op.add_column("roles", sa.Column("updated_by", sa.Integer(), nullable=True))
    op.add_column("roles", sa.Column("deleted_by", sa.Integer(), nullable=True))

    op.create_foreign_key(
        "fk_roles_created_by_users",
        "roles",
        "users",
        ["created_by"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_roles_updated_by_users",
        "roles",
        "users",
        ["updated_by"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_roles_deleted_by_users",
        "roles",
        "users",
        ["deleted_by"],
        ["id"],
        ondelete="SET NULL",
    )

    # permissions
    op.add_column("permissions", sa.Column("created_by", sa.Integer(), nullable=True))
    op.add_column("permissions", sa.Column("updated_by", sa.Integer(), nullable=True))
    op.add_column("permissions", sa.Column("deleted_by", sa.Integer(), nullable=True))

    op.create_foreign_key(
        "fk_permissions_created_by_users",
        "permissions",
        "users",
        ["created_by"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_permissions_updated_by_users",
        "permissions",
        "users",
        ["updated_by"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_permissions_deleted_by_users",
        "permissions",
        "users",
        ["deleted_by"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    # permissions
    op.drop_constraint("fk_permissions_deleted_by_users", "permissions", type_="foreignkey")
    op.drop_constraint("fk_permissions_updated_by_users", "permissions", type_="foreignkey")
    op.drop_constraint("fk_permissions_created_by_users", "permissions", type_="foreignkey")
    op.drop_column("permissions", "deleted_by")
    op.drop_column("permissions", "updated_by")
    op.drop_column("permissions", "created_by")

    # roles
    op.drop_constraint("fk_roles_deleted_by_users", "roles", type_="foreignkey")
    op.drop_constraint("fk_roles_updated_by_users", "roles", type_="foreignkey")
    op.drop_constraint("fk_roles_created_by_users", "roles", type_="foreignkey")
    op.drop_column("roles", "deleted_by")
    op.drop_column("roles", "updated_by")
    op.drop_column("roles", "created_by")