"""add timezone to users

Revision ID: 4a5b6c7d8e9f
Revises: 9n0o1p2q3r4s
Create Date: 2026-01-17 18:50:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4a5b6c7d8e9f'
down_revision = '9n0o1p2q3r4s'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add timezone column to users table with default value
    # Using server_default for SQLite compatibility
    op.add_column('users', sa.Column('timezone', sa.String(length=50),
                                      nullable=False,
                                      server_default='Europe/Warsaw'))


def downgrade() -> None:
    op.drop_column('users', 'timezone')
