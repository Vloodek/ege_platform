from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.inspection import inspect
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

# Модель урока
class Lesson(Base):
    __tablename__ = 'lessons'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    videoLink = Column(String, nullable=True)
    text = Column(Text)
    files = Column(Text, nullable=True)
    image_links = Column(Text, nullable=True)  # Новая колонка для хранения ссылок на изображения
    date = Column(DateTime, default=datetime.utcnow)

    # Связь с домашними заданиями
    homeworks = relationship("Homework", back_populates="lesson")


# Модель домашнего задания
class Homework(Base):
    __tablename__ = 'homeworks'

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), index=True)  # Внешний ключ на таблицу Lesson
    description = Column(Text)
    files = Column(Text, nullable=True)  # Места для хранения файлов
    date = Column(DateTime, default=datetime.utcnow)
    text = Column(Text)

    # Связь с уроком
    lesson = relationship("Lesson", back_populates="homeworks")  # Связь с уроком

class SessionToken(Base):
    __tablename__ = "session_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    token = Column(String, unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)  # Время истечения токена

    # Связь с пользователем
    user = relationship("User", back_populates="tokens")


# Связь с пользователем
User.tokens = relationship("SessionToken", back_populates="user", cascade="all, delete-orphan")

def init_db():
    """Создание таблиц в базе данных"""
    inspector = inspect(engine)
    if not inspector.has_table("users"):
        Base.metadata.create_all(bind=engine)
    if not inspector.has_table("lessons"):  # Проверяем существование таблицы lessons
        Base.metadata.create_all(bind=engine)
    if not inspector.has_table("homeworks"):  # Проверяем существование таблицы homeworks
        Base.metadata.create_all(bind=engine)
    existing_tables = inspector.get_table_names()

    for table_name in Base.metadata.tables.keys():
        if table_name not in existing_tables:
            Base.metadata.tables[table_name].create(bind=engine)
