"""Initial migration

Revision ID: 27ff5d354abc
Revises: 5527d246dd38
Create Date: 2025-03-22 13:02:06.951237

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '27ff5d354abc'
down_revision: Union[str, None] = '5527d246dd38'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
