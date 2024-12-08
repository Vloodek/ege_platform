from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime,ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship  # Добавлен relationship, если не было
from sqlalchemy.inspection import inspect  # Импортируем inspect
from datetime import datetime

# Убедитесь, что путь к базе данных указан правильно
DATABASE_URL = "sqlite:///E:/ege_platform/platfrom/backend/test.db"


engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Модель пользователя
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String, default="student")  # Поле для роли пользователя (student/teacher)

# Модель задания
class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    videoLink = Column(String, nullable=True)
    text = Column(Text)
    files = Column(Text, nullable=True)  # Сохраняем имена файлов в виде строки или JSON
    date = Column(DateTime, default=datetime.utcnow)

    # Добавляем связь с Homework
    homeworks = relationship("Homework", back_populates="task")  # Устанавливаем связь

# Модель домашнего задания
class Homework(Base):
    __tablename__ = 'homeworks'

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), index=True)  # Ссылка на задание
    description = Column(Text)
    files = Column(Text, nullable=True)  # Места для хранения файлов
    date = Column(DateTime, default=datetime.utcnow)
    text = Column(Text)

    task = relationship("Task", back_populates="homeworks")  # Связь с заданием

def init_db():
    """Создание таблиц в базе данных"""
    inspector = inspect(engine)
    if not inspector.has_table("users"):
        Base.metadata.create_all(bind=engine)
    if not inspector.has_table("tasks"):
        Base.metadata.create_all(bind=engine)
    if not inspector.has_table("lessons"):  # Проверяем существование таблицы lessons
        Base.metadata.create_all(bind=engine)
    existing_tables = inspector.get_table_names()

    for table_name in Base.metadata.tables.keys():
        if table_name not in existing_tables:
            Base.metadata.tables[table_name].create(bind=engine)

