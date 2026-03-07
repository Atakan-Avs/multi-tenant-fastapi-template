"""add user role

Revision ID: 8d8ae295bd84
Revises: 523675497f48
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "8d8ae295bd84"
down_revision = "523675497f48"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1) nullable ekle (mevcut satırlar patlamasın)
    op.add_column("users", sa.Column("role", sa.String(length=20), nullable=True))

    # 2) eski kayıtları doldur
    op.execute("UPDATE users SET role = 'member' WHERE role IS NULL")

    # 3) NOT NULL yap
    op.alter_column("users", "role", nullable=False)


def downgrade() -> None:
    op.drop_column("users", "role")

