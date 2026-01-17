"""add audit logs table

Revision ID: 9n0o1p2q3r4s
Revises: 1e2f3g4h5i6j
Create Date: 2026-01-17 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON


# revision identifiers, used by Alembic.
revision = '9n0o1p2q3r4s'
down_revision = '1e2f3g4h5i6j'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create audit_logs table"""
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.String(36), primary_key=True),  # UUID as string for SQLite compatibility
        sa.Column('user_id', sa.String(36), nullable=False),  # UUID as string
        sa.Column('user_email', sa.String(255), nullable=False),
        sa.Column('action_type', sa.String(100), nullable=False),
        sa.Column('resource_type', sa.String(50), nullable=False),
        sa.Column('resource_id', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.Text, nullable=True),
        sa.Column('extra_data', sa.Text, nullable=True),  # JSON as text for SQLite
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    # Create indexes for common queries
    op.create_index('ix_audit_logs_user_id', 'audit_logs', ['user_id'])
    op.create_index('ix_audit_logs_action_type', 'audit_logs', ['action_type'])
    op.create_index('ix_audit_logs_resource_id', 'audit_logs', ['resource_id'])
    op.create_index('ix_audit_logs_created_at', 'audit_logs', ['created_at'])


def downgrade() -> None:
    """Drop audit_logs table"""
    op.drop_index('ix_audit_logs_created_at', table_name='audit_logs')
    op.drop_index('ix_audit_logs_resource_id', table_name='audit_logs')
    op.drop_index('ix_audit_logs_action_type', table_name='audit_logs')
    op.drop_index('ix_audit_logs_user_id', table_name='audit_logs')
    op.drop_table('audit_logs')
