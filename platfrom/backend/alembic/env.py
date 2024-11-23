# alembic/env.py
from __future__ import with_statement
import sys
import os
from logging.config import fileConfig

from sqlalchemy import create_engine, pool
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base
from alembic import context

# Импортируем ваши модели
from app.database import Base  # Убедитесь, что путь правильный

# Это необходимо для правильной работы с миграциями
target_metadata = Base.metadata  # Указываем, что MetaData для Alembic берется из Base

# Эта часть кода обычно не меняется, и Alembic будет работать с вашей базой
config = context.config
fileConfig(config.config_file_name)

# ...

# Инициализация соединения с базой данных
def run_migrations_offline():
    # Сюда вставьте ваш код для миграций, если необходимо
    pass

def run_migrations_online():
    # Сюда вставьте ваш код для работы онлайн
    pass

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
