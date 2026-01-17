"""add_two_factor_auth_fields

Revision ID: 1e2f3g4h5i6j
Revises: 0d6dd5b7f9af
Create Date: 2026-01-17 05:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1e2f3g4h5i6j'
down_revision: Union[str, None] = '0d6dd5b7f9af'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add two-factor authentication fields to users table
    op.add_column('users', sa.Column('totp_secret', sa.String(length=32), nullable=True))
    op.add_column('users', sa.Column('two_factor_enabled', sa.Boolean(), nullable=False, server_default='false'))


def downgrade() -> None:
    # Remove two-factor authentication fields
    op.drop_column('users', 'two_factor_enabled')
    op.drop_column('users', 'totp_secret')
