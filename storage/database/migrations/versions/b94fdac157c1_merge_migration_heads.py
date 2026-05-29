"""merge migration heads

Revision ID: b94fdac157c1
Revises: 557bbd1b471b, 3883f2b9881a
Create Date: 2026-05-29 23:24:07.278152

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b94fdac157c1'
down_revision: Union[str, Sequence[str], None] = ('557bbd1b471b', '3883f2b9881a')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
