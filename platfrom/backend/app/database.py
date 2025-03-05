# database.py
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

# DATABASE_URL = "sqlite:///E:/ege_platform/platfrom/backend/test.db"
DATABASE_URL = "mysql+pymysql://root:ink-rooted-se1337@localhost:3306/ink"


engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True)
    code = Column(String(10), unique=True, index=True)  # Уникальный код (до 10 символов)
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("User", back_populates="group")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    email = Column(String(255), unique=True, index=True)
    password = Column(String(255))  # Пароль может быть хешированным, задаем длину
    role = Column(String(50), default="student")  # student/teacher
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)

    group = relationship("Group", back_populates="users")

class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    description = Column(Text)
    videoLink = Column(String(500), nullable=True)  # Длина URL обычно больше стандартных 255
    text = Column(Text)
    files = Column(Text, nullable=True)
    image_links = Column(Text, nullable=True)
    date = Column(DateTime, default=datetime.utcnow)
    homeworks = relationship("Homework", back_populates="lesson")
    group_id = Column(Integer, ForeignKey("groups.id"), index=True)
    group = relationship("Group")

class Homework(Base):
    __tablename__ = "homeworks"

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), index=True)
    description = Column(Text)
    files = Column(Text, nullable=True)
    images = Column(Text, default="[]")  # Добавляем поле для хранения JSON с картинками
    date = Column(DateTime, default=datetime.utcnow)
    text = Column(Text)
    group_id = Column(Integer, ForeignKey("groups.id"), index=True)
    lesson = relationship("Lesson", back_populates="homeworks")
    group = relationship("Group")
# Таблица для отправленных домашних заданий
class HomeworkSubmission(Base):
    __tablename__ = "homework_submissions"

    id = Column(Integer, primary_key=True, index=True)
    homework_id = Column(Integer, ForeignKey("homeworks.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    submission_date = Column(DateTime, default=datetime.utcnow)  # серверное время отправки
    client_submission_time = Column(DateTime, nullable=True)      # клиентское время отправки
    grade = Column(Integer, nullable=True)
    status = Column(String(50), default="submitted")  # submitted, graded, pending
    comment = Column(Text, nullable=True)

    user = relationship("User")
    homework = relationship("Homework")


# Таблица для файлов, прикрепленных к отправленным домашкам
class HomeworkFile(Base):
    __tablename__ = "homework_files"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("homework_submissions.id"))
    file_path = Column(String(500))  # Указываем 500, если файлы хранятся по длинным путям
    file_type = Column(String(50))
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    submission = relationship("HomeworkSubmission")

# Таблица для истории оценок
class Grade(Base):
    __tablename__ = "grades"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("homework_submissions.id"))
    grade = Column(Integer)
    graded_at = Column(DateTime, default=datetime.utcnow)

    submission = relationship("HomeworkSubmission")

def init_db():
    Base.metadata.create_all(bind=engine)