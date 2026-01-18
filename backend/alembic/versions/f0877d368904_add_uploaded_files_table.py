"""add uploaded_files table

Revision ID: f0877d368904
Revises: e9766c257893
Create Date: 2026-01-18 06:15:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'f0877d368904'
down_revision = 'e9766c257893'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'uploaded_files',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('original_name', sa.String(255), nullable=False),
        sa.Column('file_path', sa.String(500), nullable=False),
        sa.Column('file_type', sa.String(50), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('extracted_content', sa.Text(), nullable=True),
        sa.Column('file_metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('conversation_id', sa.String(255), nullable=True),
    )

    # Create indexes
    op.create_index('ix_uploaded_files_user_id', 'uploaded_files', ['user_id'])
    op.create_index('ix_uploaded_files_conversation_id', 'uploaded_files', ['conversation_id'])


def downgrade() -> None:
    op.drop_index('ix_uploaded_files_conversation_id', table_name='uploaded_files')
    op.drop_index('ix_uploaded_files_user_id', table_name='uploaded_files')
    op.drop_table('uploaded_files')
