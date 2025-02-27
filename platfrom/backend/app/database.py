# database.py
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

DATABASE_URL = "sqlite:///E:/ege_platform/platfrom/backend/test.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String, default="student")  # student/teacher

class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    videoLink = Column(String, nullable=True)
    text = Column(Text)
    files = Column(Text, nullable=True)
    image_links = Column(Text, nullable=True)
    date = Column(DateTime, default=datetime.utcnow)

    homeworks = relationship("Homework", back_populates="lesson")

class Homework(Base):
    __tablename__ = "homeworks"

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), index=True)
    description = Column(Text)
    files = Column(Text, nullable=True)
    date = Column(DateTime, default=datetime.utcnow)
    text = Column(Text)

    lesson = relationship("Lesson", back_populates="homeworks")

# Новая таблица для отправленных домашних заданий
class HomeworkSubmission(Base):
    __tablename__ = "homework_submissions"

    id = Column(Integer, primary_key=True, index=True)
    homework_id = Column(Integer, ForeignKey("homeworks.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    submission_date = Column(DateTime, default=datetime.utcnow)
    grade = Column(Integer, nullable=True)
    status = Column(String, default="submitted")  # submitted, graded, pending
    comment = Column(Text, nullable=True)  # Добавляем поле comment

    user = relationship("User")
    homework = relationship("Homework")


# Новая таблица для файлов, прикрепленных к отправленным домашкам
class HomeworkFile(Base):
    __tablename__ = "homework_files"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("homework_submissions.id"))
    file_path = Column(String)
    file_type = Column(String)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    submission = relationship("HomeworkSubmission")

# Новая таблица для истории оценок
class Grade(Base):
    __tablename__ = "grades"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("homework_submissions.id"))
    grade = Column(Integer)
    graded_at = Column(DateTime, default=datetime.utcnow)

    submission = relationship("HomeworkSubmission")

def init_db():
    Base.metadata.create_all(bind=engine)
