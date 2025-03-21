"""Д

Revision ID: 1b94b74b6f90
Revises: 51a9a0b555c5
Create Date: 2025-03-10 14:25:03.151588

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '1b94b74b6f90'
down_revision: Union[str, None] = '51a9a0b555c5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('homework_submissions', sa.Column('student_submission_time', sa.DateTime(), nullable=True))
    op.drop_column('homework_submissions', 'client_submission_time')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('homework_submissions', sa.Column('client_submission_time', mysql.DATETIME(), nullable=True))
    op.drop_column('homework_submissions', 'student_submission_time')
    # ### end Alembic commands ###
