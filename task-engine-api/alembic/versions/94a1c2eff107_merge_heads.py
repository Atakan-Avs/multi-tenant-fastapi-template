"""merge heads

Revision ID: 94a1c2eff107
Revises: 4152aa93a672, 425a546761b3
Create Date: 2026-02-14 22:53:20.419236

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '94a1c2eff107'
down_revision: Union[str, Sequence[str], None] = ('4152aa93a672', '425a546761b3')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
