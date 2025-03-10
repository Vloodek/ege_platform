# database.py
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

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
    group_id = Column(Integer, ForeignKey("groups.id"), index=True)  # Новое поле для групп
    group = relationship("Group")
    homeworks = relationship("Homework", back_populates="lesson")

class Homework(Base):
    __tablename__ = "homeworks"

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), index=True)
    description = Column(Text)
    files = Column(Text, nullable=True)
    images = Column(Text, default="[]")  # Добавляем поле для хранения JSON с картинками
    date = Column(DateTime, default=datetime.utcnow)
    text = Column(Text)
    group_id = Column(Integer, ForeignKey("groups.id"), index=True)  # Новое поле для групп
    lesson = relationship("Lesson", back_populates="homeworks")
    group = relationship("Group")

    status = Column(Enum("dosed", "current", name="homework_status"), default="current")  # Новый статус

# Таблица для отправленных домашних заданий
class HomeworkSubmission(Base):
    __tablename__ = "homework_submissions"

    id = Column(Integer, primary_key=True, index=True)
    homework_id = Column(Integer, ForeignKey("homeworks.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    client_submission_time = Column(DateTime, nullable=True)  # Время отправки домашки
    modified_submission_time = Column(DateTime, nullable=True)  # Время последнего изменения отклика
    grade = Column(Integer, nullable=True)
    status = Column(Enum("submitted", "graded", "pending", "checked", name="submission_status"), default="submitted")  # Статус
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

class TeacherResponse(Base):
    __tablename__ = "teacher_responses"
    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("homework_submissions.id"), unique=True)
    teacher_comment = Column(Text, nullable=True)
    response_date = Column(DateTime, default=datetime.utcnow)
    submission = relationship("HomeworkSubmission", backref="teacher_response")

class TeacherResponseFile(Base):
    __tablename__ = "teacher_response_files"
    id = Column(Integer, primary_key=True, index=True)
    teacher_response_id = Column(Integer, ForeignKey("teacher_responses.id"))
    file_path = Column(String(500))
    file_type = Column(String(50))
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    teacher_response = relationship("TeacherResponse", backref="files")

def init_db():
    Base.metadata.create_all(bind=engine)
