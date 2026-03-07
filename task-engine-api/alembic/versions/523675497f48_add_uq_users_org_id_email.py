"""add uq users org_id email

Revision ID: 523675497f48
Revises: 16275dc15c79
Create Date: 2026-02-12 23:59:56.197799
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa  # noqa: F401


# revision identifiers, used by Alembic.
revision: str = "523675497f48"
down_revision: Union[str, Sequence[str], None] = "16275dc15c79"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1) nullable ekle (mevcut satırlar patlamasın)
    op.add_column("users", sa.Column("role", sa.String(length=20), nullable=True))

    # 2) eski kayıtları member yap
    op.execute("UPDATE users SET role = 'member' WHERE role IS NULL")

    # 3) NOT NULL yap
    op.alter_column("users", "role", nullable=False)


def downgrade() -> None:
    op.drop_column("users", "role")