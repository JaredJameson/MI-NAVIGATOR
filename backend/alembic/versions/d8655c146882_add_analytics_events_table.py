"""add analytics events table

Revision ID: d8655c146882
Revises: c7544b035771
Create Date: 2026-01-17 20:55:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB


# revision identifiers, used by Alembic.
revision = 'd8655c146882'
down_revision = 'c7544b035771'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create analytics_events table"""
    op.create_table(
        'analytics_events',
        sa.Column('id', sa.String(36), primary_key=True),  # UUID as string for SQLite compatibility
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('event_name', sa.String(100), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=True),  # UUID as string, nullable for anonymous events
        sa.Column('session_id', sa.String(100), nullable=True),
        sa.Column('event_metadata', sa.Text, nullable=True),  # JSON as text for SQLite (renamed from 'metadata' - reserved word)
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    # Create indexes for common queries
    op.create_index('ix_analytics_events_event_type', 'analytics_events', ['event_type'])
    op.create_index('ix_analytics_events_user_id', 'analytics_events', ['user_id'])
    op.create_index('ix_analytics_events_session_id', 'analytics_events', ['session_id'])
    op.create_index('ix_analytics_events_created_at', 'analytics_events', ['created_at'])


def downgrade() -> None:
    """Drop analytics_events table"""
    op.drop_index('ix_analytics_events_created_at', table_name='analytics_events')
    op.drop_index('ix_analytics_events_session_id', table_name='analytics_events')
    op.drop_index('ix_analytics_events_user_id', table_name='analytics_events')
    op.drop_index('ix_analytics_events_event_type', table_name='analytics_events')
    op.drop_table('analytics_events')
