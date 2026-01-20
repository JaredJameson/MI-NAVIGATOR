"""add webhooks table

Revision ID: a1988e479015
Revises: f0877d368904
Create Date: 2026-01-20 04:15:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a1988e479015'
down_revision = 'f0877d368904'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'webhooks',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('url', sa.String(500), nullable=False),
        sa.Column('event_type', sa.Enum('report.created', 'report.updated', 'report.deleted', 'analysis.completed', 'alert.triggered', name='webhookevent'), nullable=False),
        sa.Column('secret', sa.String(128), nullable=True),  # HMAC secret for signature verification
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('max_retries', sa.Integer(), default=5, nullable=False),
        sa.Column('retry_count', sa.Integer(), default=0, nullable=False),
        sa.Column('status', sa.Enum('pending', 'delivered', 'failed', 'retrying', name='webhookstatus'), default='pending', nullable=False),
        sa.Column('last_triggered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_delivered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_error', sa.Text(), nullable=True),
        sa.Column('next_retry_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Create indexes
    op.create_index('ix_webhooks_user_id', 'webhooks', ['user_id'])
    op.create_index('ix_webhooks_event_type', 'webhooks', ['event_type'])
    op.create_index('ix_webhooks_status', 'webhooks', ['status'])


def downgrade() -> None:
    op.drop_index('ix_webhooks_status', table_name='webhooks')
    op.drop_index('ix_webhooks_event_type', table_name='webhooks')
    op.drop_index('ix_webhooks_user_id', table_name='webhooks')
    op.drop_table('webhooks')
    op.execute('DROP TYPE webhookevent')
    op.execute('DROP TYPE webhookstatus')
