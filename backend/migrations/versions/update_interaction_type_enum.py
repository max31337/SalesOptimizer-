"""update interaction type enum

Revision ID: update_interaction_type_enum
Revises: your_previous_revision
Create Date: 2023-11-14 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'update_interaction_type_enum'
down_revision = 'your_previous_revision'  # replace with your last migration revision
branch_labels = None
depends_on = None

def upgrade():
    # Create a new enum type
    op.execute("ALTER TYPE interactiontype RENAME TO interactiontype_old")
    op.execute("CREATE TYPE interactiontype AS ENUM ('CALL', 'EMAIL', 'MEETING')")
    
    # Update the column to use the new enum type
    op.execute("ALTER TABLE interactions ALTER COLUMN type TYPE interactiontype USING type::text::interactiontype")
    
    # Drop the old enum type
    op.execute("DROP TYPE interactiontype_old")

def downgrade():
    # Create the old enum type
    op.execute("ALTER TYPE interactiontype RENAME TO interactiontype_new")
    op.execute("CREATE TYPE interactiontype AS ENUM ('call', 'email', 'meeting')")
    
    # Update the column to use the old enum type
    op.execute("ALTER TABLE interactions ALTER COLUMN type TYPE interactiontype USING type::text::interactiontype")
    
    # Drop the new enum type
    op.execute("DROP TYPE interactiontype_new")