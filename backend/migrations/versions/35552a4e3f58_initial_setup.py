from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String

# revision identifiers, used by Alembic.
revision = '35552a4e3f58'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Upgrade schema."""
    # Add the username column with a default value for existing rows
    op.add_column('users', sa.Column('username', sa.String(), nullable=False, server_default='default_username'))

    # Create a temporary table object to perform updates
    users_table = table('users', column('id', sa.Integer), column('username', sa.String))

    # Update each row with a unique username
    conn = op.get_bind()
    result = conn.execute(users_table.select())
    for i, row in enumerate(result):
        conn.execute(users_table.update().where(users_table.c.id == row.id).values(username=f'user_{i}'))

    # Remove the server default after updating
    op.alter_column('users', 'username', server_default=None)

    # Create unique constraint
    op.create_unique_constraint(None, 'users', ['username'])

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(None, 'users', type_='unique')
    op.drop_column('users', 'username')
