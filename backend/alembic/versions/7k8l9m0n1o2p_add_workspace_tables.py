"""add_workspace_tables

Revision ID: 7k8l9m0n1o2p
Revises: 6f7g8h9i0j1k
Create Date: 2026-01-17 00:10:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '7k8l9m0n1o2p'
down_revision = '6f7g8h9i0j1k'
branch_labels = None
depends_on = None


def upgrade():
    # Create workspaces table
    op.create_table(
        'workspaces',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('owner_id', sa.String(36), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('settings', sa.Text(), nullable=True),  # JSON stored as text for SQLite
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], name='fk_workspaces_owner_id_users', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_workspaces')
    )

    # Create workspace_members table
    op.create_table(
        'workspace_members',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('workspace_id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('role', sa.Enum('OWNER', 'ADMIN', 'MEMBER', 'VIEWER', name='workspacememberrole'), nullable=False),
        sa.Column('invited_by', sa.String(36), nullable=True),
        sa.Column('invitation_accepted', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('last_active_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name='fk_workspace_members_workspace_id_workspaces', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_workspace_members_user_id_users', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['invited_by'], ['users.id'], name='fk_workspace_members_invited_by_users', ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id', name='pk_workspace_members')
    )

    # Create indexes
    op.create_index('ix_workspace_members_workspace_id', 'workspace_members', ['workspace_id'])
    op.create_index('ix_workspace_members_user_id', 'workspace_members', ['user_id'])


def downgrade():
    # Drop indexes
    op.drop_index('ix_workspace_members_user_id', table_name='workspace_members')
    op.drop_index('ix_workspace_members_workspace_id', table_name='workspace_members')

    # Drop tables
    op.drop_table('workspace_members')
    op.drop_table('workspaces')

    # Drop enum
    op.execute('DROP TYPE workspacememberrole')
