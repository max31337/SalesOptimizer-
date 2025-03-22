"""Initial migration

Revision ID: 5527d246dd38
Revises: aaea5ff33694
Create Date: 2025-03-22 12:58:19.422742

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5527d246dd38'
down_revision: Union[str, None] = 'aaea5ff33694'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
