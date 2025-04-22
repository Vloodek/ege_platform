"""Добалено тестирование для домашек

Revision ID: 5f55e971b1f5
Revises: abd90041dfe3
Create Date: 2025-04-21 13:40:41.285840

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '5f55e971b1f5'
down_revision: Union[str, None] = 'abd90041dfe3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Добавляем lesson_id
    op.add_column('homework_tests', sa.Column('lesson_id', sa.Integer(), nullable=False))

    # 2. Создаём индекс на lesson_id
    op.create_index(op.f('ix_homework_tests_lesson_id'), 'homework_tests', ['lesson_id'], unique=False)

    # 3. Создаём внешний ключ на lesson_id
    op.create_foreign_key(None, 'homework_tests', 'lessons', ['lesson_id'], ['id'], ondelete='CASCADE')

    # 4. Удаляем колонку homework_id
    op.drop_column('homework_tests', 'homework_id')

def downgrade() -> None:
    # 1. Добавляем обратно колонку homework_id
    op.add_column('homework_tests', sa.Column('homework_id', mysql.INTEGER(), autoincrement=False, nullable=False))

    # 2. Удаляем внешний ключ
    op.drop_constraint(None, 'homework_tests', type_='foreignkey')

    # 3. Создаём внешний ключ обратно на homework_id
    op.create_foreign_key('homework_tests_ibfk_1', 'homework_tests', 'homeworks', ['homework_id'], ['id'], ondelete='CASCADE')

    # 4. Удаляем индекс на lesson_id
    op.drop_index(op.f('ix_homework_tests_lesson_id'), table_name='homework_tests')

    # 5. Создаём индекс обратно на homework_id
    op.create_index('ix_homework_tests_homework_id', 'homework_tests', ['homework_id'], unique=False)

    # 6. Удаляем колонку lesson_id
    op.drop_column('homework_tests', 'lesson_id')

