"""fix interaction enum

Revision ID: fix_interaction_enum
Revises: update_interaction_type_enum
Create Date: 2023-11-14 10:00:00.000000
"""
from alembic import op

# revision identifiers, used by Alembic.
revision = 'fix_interaction_enum'
down_revision = 'update_interaction_type_enum'
branch_labels = None
depends_on = None

def upgrade():
    # No changes needed as enum is already correct
    pass

def downgrade():
    # No changes to revert
    pass