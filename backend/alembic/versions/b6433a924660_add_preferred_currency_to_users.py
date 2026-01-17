"""add_preferred_currency_to_users

Revision ID: b6433a924660
Revises: 4a5b6c7d8e9f
Create Date: 2026-01-17 19:39:27.314016

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b6433a924660'
down_revision: Union[str, None] = '4a5b6c7d8e9f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add preferred_currency column to users table
    op.add_column('users', sa.Column('preferred_currency', sa.String(3), server_default='PLN', nullable=False))


def downgrade() -> None:
    # Remove preferred_currency column from users table
    op.drop_column('users', 'preferred_currency')
