"""update interaction type enum

Revision ID: update_interaction_type_enum
Revises: c2bd9d4ca53d
Create Date: 2023-11-14 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'update_interaction_type_enum'
down_revision = 'c2bd9d4ca53d'  # This should match your initial migration ID
branch_labels = None
depends_on = None

def upgrade():
    # Safely handle the enum type update
    op.execute("""
    DO $$
    BEGIN
        IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'interactiontype') THEN
            ALTER TYPE interactiontype RENAME TO interactiontype_old;
        END IF;
    EXCEPTION WHEN OTHERS THEN
        -- Type might be in use, handle gracefully
        NULL;
    END $$;
    """)
    
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'interactiontype') THEN
            CREATE TYPE interactiontype AS ENUM ('CALL', 'EMAIL', 'MEETING');
        END IF;
    END $$;
    """)
    
    # Update the column to use the new enum type
    op.execute("ALTER TABLE IF EXISTS interactions ALTER COLUMN type TYPE interactiontype USING type::text::interactiontype")
    
    # Safely drop the old enum type
    op.execute("""
    DO $$
    BEGIN
        DROP TYPE IF EXISTS interactiontype_old;
    EXCEPTION WHEN OTHERS THEN
        NULL;
    END $$;
    """)

def downgrade():
    # Similar safe handling for downgrade
    op.execute("""
    DO $$
    BEGIN
        IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'interactiontype') THEN
            ALTER TYPE interactiontype RENAME TO interactiontype_new;
        END IF;
    END $$;
    """)
    
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'interactiontype') THEN
            CREATE TYPE interactiontype AS ENUM ('call', 'email', 'meeting');
        END IF;
    END $$;
    """)
    
    op.execute("ALTER TABLE IF EXISTS interactions ALTER COLUMN type TYPE interactiontype USING type::text::interactiontype")
    
    op.execute("DROP TYPE IF EXISTS interactiontype_new")
    # Create a new enum type
    op.execute("ALTER TYPE interactiontype RENAME TO interactiontype_old")
    op.execute("CREATE TYPE interactiontype AS ENUM ('CALL', 'EMAIL', 'MEETING')")
    
    # Update the column to use the new enum type
    op.execute("ALTER TABLE interactions ALTER COLUMN type TYPE interactiontype USING type::text::interactiontype")
    
    # Drop the old enum type
    op.execute("DROP TYPE interactiontype_old")