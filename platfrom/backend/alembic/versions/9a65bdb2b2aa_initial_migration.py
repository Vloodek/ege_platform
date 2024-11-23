"""Initial migration

Revision ID: 9a65bdb2b2aa
Revises: 
Create Date: 2024-11-20 17:04:35.906883

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9a65bdb2b2aa'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
