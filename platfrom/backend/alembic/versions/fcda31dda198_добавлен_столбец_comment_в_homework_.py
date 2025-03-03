"""Добавлен столбец comment в homework_submissions

Revision ID: fcda31dda198
Revises: 
Create Date: 2025-02-17 13:45:14.649994

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fcda31dda198'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_session_tokens_id', table_name='session_tokens')
    op.drop_index('ix_session_tokens_user_id', table_name='session_tokens')
    op.drop_table('session_tokens')
    op.add_column('homework_submissions', sa.Column('comment', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('homework_submissions', 'comment')
    op.create_table('session_tokens',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('user_id', sa.INTEGER(), nullable=True),
    sa.Column('token', sa.VARCHAR(), nullable=False),
    sa.Column('expires_at', sa.DATETIME(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('token')
    )
    op.create_index('ix_session_tokens_user_id', 'session_tokens', ['user_id'], unique=False)
    op.create_index('ix_session_tokens_id', 'session_tokens', ['id'], unique=False)
    # ### end Alembic commands ###
