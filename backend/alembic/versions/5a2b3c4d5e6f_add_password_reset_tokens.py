"""Add password reset tokens table

Revision ID: 5a2b3c4d5e6f
Revises: 04b18ebf5bfb
Create Date: 2026-01-15 18:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5a2b3c4d5e6f'
down_revision: Union[str, None] = '04b18ebf5bfb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('password_reset_tokens',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('token', sa.String(length=255), nullable=False),
    sa.Column('expires_at', sa.DateTime(), nullable=False),
    sa.Column('used', sa.Boolean(), nullable=True, default=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_password_reset_tokens_user_id_users'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_password_reset_tokens'))
    )
    op.create_index(op.f('ix_password_reset_tokens_token'), 'password_reset_tokens', ['token'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_password_reset_tokens_token'), table_name='password_reset_tokens')
    op.drop_table('password_reset_tokens')
