"""Add report_templates table

Revision ID: 8m9n0o1p2q3r
Revises: 7k8l9m0n1o2p
Create Date: 2026-01-17 04:10:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = '8m9n0o1p2q3r'
down_revision = '7k8l9m0n1o2p'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create report_templates table (SQLite compatible)
    op.create_table(
        'report_templates',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('type', sa.String(length=100), nullable=False),
        sa.Column('created_by', sa.String(length=36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('sections', sa.Text(), nullable=False, server_default='[]'),  # JSON as TEXT for SQLite
        sa.Column('use_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_used', sa.DateTime(), nullable=True),
        sa.Column('original_report_id', sa.String(length=100), nullable=True),
        sa.Column('original_report_title', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    # Create index on created_by for faster queries
    op.create_index('ix_report_templates_created_by', 'report_templates', ['created_by'])

    # Create index on type for filtering
    op.create_index('ix_report_templates_type', 'report_templates', ['type'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_report_templates_type', table_name='report_templates')
    op.drop_index('ix_report_templates_created_by', table_name='report_templates')

    # Drop table
    op.drop_table('report_templates')
