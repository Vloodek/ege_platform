"""Добавил что-тоs

Revision ID: 1667883fb6d0
Revises: 8ed0425c5b3c
Create Date: 2025-03-10 16:02:05.197456

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1667883fb6d0'
down_revision: Union[str, None] = '8ed0425c5b3c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
