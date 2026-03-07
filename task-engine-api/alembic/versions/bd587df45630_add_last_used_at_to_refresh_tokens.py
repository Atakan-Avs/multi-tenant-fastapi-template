"""add last_used_at to refresh_tokens

Revision ID: bd587df45630
Revises: 68959be4c538
Create Date: 2026-02-24 19:20:10.730128

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bd587df45630'
down_revision: Union[str, Sequence[str], None] = '68959be4c538'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("refresh_tokens", sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True))



def downgrade() -> None:
    op.drop_column("refresh_tokens", "last_used_at")