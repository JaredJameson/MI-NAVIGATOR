"""add_secret_to_existing_webhooks_table

Revision ID: 448eb031eb12
Revises: g1988f479abc
Create Date: 2026-01-20 07:41:22.544712

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '448eb031eb12'
down_revision: Union[str, None] = 'g1988f479abc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add secret column to existing webhooks table
    # Using try/except to handle if column already exists
    try:
        op.add_column('webhooks', sa.Column('secret', sa.String(128), nullable=True))
    except Exception:
        # Column might already exist, that's ok
        pass


def downgrade() -> None:
    # Remove secret column
    try:
        op.drop_column('webhooks', 'secret')
    except Exception:
        pass
