from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Enum, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

DATABASE_URL = "mysql+pymysql://root:ink-rooted-se1337@localhost:3306/ink"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Промежуточная таблица для связи уроков с группами
lesson_groups = Table(
    "lesson_groups",
    Base.metadata,
    Column("lesson_id", Integer, ForeignKey("lessons.id"), primary_key=True),
    Column("group_id", Integer, ForeignKey("study_groups.id"), primary_key=True)  # Заменено на study_groups
)

# Промежуточная таблица для связи домашних заданий с группами
homework_groups = Table(
    "homework_groups",
    Base.metadata,
    Column("homework_id", Integer, ForeignKey("homeworks.id"), primary_key=True),
    Column("group_id", Integer, ForeignKey("study_groups.id"), primary_key=True)  # Заменено на study_groups
)


class StudyGroup(Base):
    __tablename__ = "study_groups"  # Переименовали таблицу, чтобы избежать конфликтов с зарезервированными словами

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True)
    code = Column(String(10), unique=True, index=True)  # Уникальный код (до 10 символов)
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("User", back_populates="group")
    lessons = relationship("Lesson", secondary=lesson_groups, back_populates="groups")
    homeworks = relationship("Homework", secondary=homework_groups, back_populates="groups")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    email = Column(String(255), unique=True, index=True)
    password = Column(String(255))
    role = Column(String(50), default="student")  # student/teacher
    group_id = Column(Integer, ForeignKey("study_groups.id"), nullable=True)
    total_points = Column(Integer, default=0, server_default="0")


    group = relationship("StudyGroup", back_populates="users")
    refresh_tokens = relationship("RefreshToken", back_populates="user")


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    description = Column(Text)
    videoLink = Column(String(500), nullable=True)  # Длина URL может превышать 255 символов
    text = Column(Text)
    files = Column(Text, nullable=True)
    image_links = Column(Text, nullable=True)
    date = Column(DateTime, default=datetime.utcnow)
    
    # Связь "многие ко многим" с группами через промежуточную таблицу lesson_groups
    groups = relationship("StudyGroup", secondary=lesson_groups, back_populates="lessons")
    homeworks = relationship("Homework", back_populates="lesson")

class Homework(Base):
    __tablename__ = "homeworks"

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), index=True)
    description = Column(Text)
    files = Column(Text, nullable=True)
    images = Column(Text, default="[]")  # Поле для хранения JSON с картинками
    date = Column(DateTime, default=datetime.utcnow)
    text = Column(Text)
    
    # Связь "многие ко многим" с группами через промежуточную таблицу homework_groups
    groups = relationship("StudyGroup", secondary=homework_groups, back_populates="homeworks")
    lesson = relationship("Lesson", back_populates="homeworks")
    
    status = Column(Enum("dosed", "current", name="homework_status"), default="current")  # Новый статус

# Таблица для отправленных домашних заданий
class HomeworkSubmission(Base):
    __tablename__ = "homework_submissions"

    id = Column(Integer, primary_key=True, index=True)
    homework_id = Column(Integer, ForeignKey("homeworks.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    student_submission_time = Column(DateTime, nullable=True)
    modified_submission_time = Column(DateTime, nullable=True)
    grade = Column(Integer, nullable=True)
    status = Column(Enum("submitted", "graded", "response_received", "waiting", name="submission_status"), default="submitted")
    comment = Column(Text, nullable=True)

    user = relationship("User")
    homework = relationship("Homework")

# Таблица для файлов, прикрепленных к отправленным домашним заданиям
class HomeworkFile(Base):
    __tablename__ = "homework_files"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("homework_submissions.id"))
    file_path = Column(String(500))  # Длинный путь может занимать до 500 символов
    file_type = Column(String(255))
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
    file_type = Column(String(255))
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    teacher_response = relationship("TeacherResponse", backref="files")

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String(255), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="refresh_tokens")

def init_db():
    Base.metadata.create_all(bind=engine)
