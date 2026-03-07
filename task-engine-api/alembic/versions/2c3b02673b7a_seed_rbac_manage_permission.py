"""seed rbac.manage permission

Revision ID: 2c3b02673b7a
Revises: a7d24cf1dfe9
Create Date: 2026-02-24 20:19:09.484864

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2c3b02673b7a'
down_revision: Union[str, Sequence[str], None] = 'a7d24cf1dfe9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        INSERT INTO permissions (code, description, created_at)
        VALUES ('rbac.manage', 'Manage roles and permissions', NOW())
        ON CONFLICT (code) DO NOTHING;
    """)

    # admin role'lara bu permission'ı ekle
    op.execute("""
        INSERT INTO role_permissions (role_id, permission_id)
        SELECT r.id, p.id
        FROM roles r
        JOIN permissions p ON p.code = 'rbac.manage'
        WHERE r.name = 'admin'
        ON CONFLICT DO NOTHING;
    """)

def downgrade() -> None:
    # güvenli downgrade: ilişkileri sil, permission'ı silme (istersen silebilirsin)
    op.execute("""
        DELETE FROM role_permissions rp
        USING permissions p
        WHERE rp.permission_id = p.id AND p.code = 'rbac.manage';
    """)
