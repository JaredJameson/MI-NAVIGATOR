"""add_account_lockout_fields

Revision ID: 0d6dd5b7f9af
Revises: 8m9n0o1p2q3r
Create Date: 2026-01-17 04:52:05.307949

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0d6dd5b7f9af'
down_revision: Union[str, None] = '8m9n0o1p2q3r'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add account lockout fields to users table
    op.add_column('users', sa.Column('failed_login_attempts', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('users', sa.Column('account_locked_until', sa.DateTime(), nullable=True))


def downgrade() -> None:
    # Remove account lockout fields
    op.drop_column('users', 'account_locked_until')
    op.drop_column('users', 'failed_login_attempts')
