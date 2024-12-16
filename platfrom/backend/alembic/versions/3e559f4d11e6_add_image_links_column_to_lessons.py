"""add image_links column to lessons

Revision ID: 3e559f4d11e6
Revises: f6a15b588145
Create Date: 2024-12-14 16:59:29.670413

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3e559f4d11e6'
down_revision: Union[str, None] = 'f6a15b588145'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
