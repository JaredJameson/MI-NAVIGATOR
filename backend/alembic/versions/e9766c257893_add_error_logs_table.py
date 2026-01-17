"""add error_logs table

Revision ID: e9766c257893
Revises: d8655c146882
Create Date: 2026-01-17 21:10:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'e9766c257893'
down_revision = 'd8655c146882'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'error_logs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('error_type', sa.String(100), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=False),
        sa.Column('stack_trace', sa.Text(), nullable=True),
        sa.Column('source', sa.String(20), nullable=False),
        sa.Column('url', sa.String(500), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('user_id', sa.String(36), nullable=True),
        sa.Column('user_email', sa.String(255), nullable=True),
        sa.Column('error_metadata', sa.JSON(), nullable=True),
        sa.Column('resolved', sa.Boolean(), server_default='0', nullable=False),
        sa.Column('occurred_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Create indexes
    op.create_index('ix_error_logs_id', 'error_logs', ['id'])
    op.create_index('ix_error_logs_user_id', 'error_logs', ['user_id'])
    op.create_index('ix_error_logs_resolved', 'error_logs', ['resolved'])
    op.create_index('ix_error_logs_occurred_at', 'error_logs', ['occurred_at'])


def downgrade() -> None:
    op.drop_index('ix_error_logs_occurred_at')
    op.drop_index('ix_error_logs_resolved')
    op.drop_index('ix_error_logs_user_id')
    op.drop_index('ix_error_logs_id')
    op.drop_table('error_logs')
