"""add worker results

Revision ID: 2f6a3d9b7c10
Revises: 9ad93a2533c3
Create Date: 2026-06-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2f6a3d9b7c10'
down_revision: Union[str, Sequence[str], None] = '9ad93a2533c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'worker_results',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('asset_id', sa.String(), nullable=False),
        sa.Column('worker_type', sa.String(), nullable=False),
        sa.Column('data', sa.JSON(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['asset_id'], ['assets.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )

    op.add_column('content_chunks', sa.Column('worker_result_id', sa.String(), nullable=True))
    op.create_foreign_key(
        'fk_content_chunks_worker_result_id_worker_results',
        'content_chunks',
        'worker_results',
        ['worker_result_id'],
        ['id'],
    )
    op.alter_column('content_chunks', 'extracted_content_id', nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        'fk_content_chunks_worker_result_id_worker_results',
        'content_chunks',
        type_='foreignkey',
    )
    op.drop_column('content_chunks', 'worker_result_id')
    op.alter_column('content_chunks', 'extracted_content_id', nullable=False)
    op.drop_table('worker_results')
