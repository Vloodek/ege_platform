"""Добавил что-то

Revision ID: 8ed0425c5b3c
Revises: 8f80aa11f684
Create Date: 2025-03-10 15:47:12.905665

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8ed0425c5b3c'
down_revision: Union[str, None] = '8f80aa11f684'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Добавляем новый статус в ENUM
    op.alter_column(
        'homework_submissions',  # Название таблицы
        'status',  # Название столбца
        type_=sa.Enum("submitted", "graded", "response_received", name="submission_status"),  # Новый ENUM
        existing_type=sa.Enum("submitted", "graded", "pending", "checked", name="submission_status")  # Старый ENUM
    )


def downgrade() -> None:
    # Возвращаем старую версию ENUM
    op.alter_column(
        'homework_submissions',
        'status',
        type_=sa.Enum("submitted", "graded", "pending", "checked", name="submission_status"),  # Старый ENUM
        existing_type=sa.Enum("submitted", "graded", "response_received", name="submission_status")  # Новый ENUM
    )

