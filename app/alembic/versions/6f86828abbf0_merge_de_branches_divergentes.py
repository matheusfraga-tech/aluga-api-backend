"""Merge de branches divergentes

Revision ID: 6f86828abbf0
Revises: 47295776065e, 9fd70d7bfede
Create Date: 2025-11-02 15:09:58.004972

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6f86828abbf0'
down_revision: Union[str, Sequence[str], None] = ('47295776065e', '9fd70d7bfede')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
