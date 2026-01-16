"""add_custom_fields_tables

Revision ID: 6f7g8h9i0j1k
Revises: 5a2b3c4d5e6f
Create Date: 2026-01-16 21:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '6f7g8h9i0j1k'
down_revision = '5a2b3c4d5e6f'
branch_labels = None
depends_on = None


def upgrade():
    # Create custom_field_definitions table
    # Using String for UUID to support SQLite
    op.create_table(
        'custom_field_definitions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('field_type', sa.String(length=20), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_required', sa.Boolean(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('options', sa.Text(), nullable=True),  # JSON as text for SQLite
        sa.Column('display_order', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create custom_field_values table
    op.create_table(
        'custom_field_values',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('field_definition_id', sa.String(length=36), nullable=False),
        sa.Column('company_id', sa.String(length=100), nullable=False),
        sa.Column('value', sa.Text(), nullable=True),
        sa.Column('value_json', sa.Text(), nullable=True),  # JSON as text for SQLite
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['field_definition_id'], ['custom_field_definitions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create index on company_id for faster lookups
    op.create_index('ix_custom_field_values_company_id', 'custom_field_values', ['company_id'], unique=False)


def downgrade():
    op.drop_index('ix_custom_field_values_company_id', table_name='custom_field_values')
    op.drop_table('custom_field_values')
    op.drop_table('custom_field_definitions')
