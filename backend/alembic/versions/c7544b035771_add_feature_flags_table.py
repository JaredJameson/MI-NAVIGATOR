"""add feature_flags table

Revision ID: c7544b035771
Revises: b6433a924660
Create Date: 2026-01-17 20:25:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c7544b035771'
down_revision = 'b6433a924660'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'feature_flags',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(100), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key')
    )
    op.create_index('ix_feature_flags_key', 'feature_flags', ['key'])

    # Insert default feature flags
    op.execute("""
        INSERT INTO feature_flags (key, name, description, enabled) VALUES
        ('chat_enabled', 'Chat Feature', 'Enable chat functionality', true),
        ('advanced_analytics', 'Advanced Analytics', 'Enable advanced analytics features', true),
        ('export_reports', 'Export Reports', 'Enable report export functionality', true),
        ('maintenance_mode', 'Maintenance Mode', 'Enable maintenance mode', false)
    """)


def downgrade():
    op.drop_index('ix_feature_flags_key')
    op.drop_table('feature_flags')
