"""drop global unique email index

Revision ID: 425a546761b3
Revises: 8d8ae295bd84
Create Date: 2026-02-14 01:16:27.554228

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '425a546761b3'
down_revision: Union[str, Sequence[str], None] = '8d8ae295bd84'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index("ix_users_email", table_name="users")


def downgrade() -> None:
    op.create_index("ix_users_email", "users", ["email"], unique=True)

