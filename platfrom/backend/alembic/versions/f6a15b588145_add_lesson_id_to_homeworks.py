"""Add lesson_id to homeworks

Revision ID: f6a15b588145
Revises: 9a65bdb2b2aa
Create Date: 2024-12-08 15:48:50.880756

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f6a15b588145'
down_revision: Union[str, None] = '9a65bdb2b2aa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
