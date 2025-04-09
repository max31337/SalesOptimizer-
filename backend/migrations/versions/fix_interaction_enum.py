"""fix interaction enum

Revision ID: fix_interaction_enum
Revises: update_interaction_type_enum
Create Date: 2023-11-14 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'fix_interaction_enum'
down_revision = 'update_interaction_type_enum'
branch_labels = None
depends_on = None

def upgrade():
    # Drop existing enum type and its dependencies
    op.execute("ALTER TABLE interactions DROP CONSTRAINT IF EXISTS interactions_type_check")
    op.execute("DROP TYPE IF EXISTS interactiontype")
    
    # Create new enum type with lowercase values
    op.execute("CREATE TYPE interactiontype AS ENUM ('call', 'email', 'meeting')")
    
    # Update the column to use the new enum type
    op.execute("ALTER TABLE interactions ALTER COLUMN type TYPE interactiontype USING type::text::interactiontype")

def downgrade():
    # If needed to rollback, recreate the original enum
    op.execute("ALTER TABLE interactions DROP CONSTRAINT IF EXISTS interactions_type_check")
    op.execute("DROP TYPE IF EXISTS interactiontype")
    op.execute("CREATE TYPE interactiontype AS ENUM ('CALL', 'EMAIL', 'MEETING')")
    op.execute("ALTER TABLE interactions ALTER COLUMN type TYPE interactiontype USING type::text::interactiontype")