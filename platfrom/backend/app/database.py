from sqlalchemy import (
    create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Enum, Table
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

DATABASE_URL = "mysql+pymysql://root:ink-rooted-se1337@localhost:3306/ink"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Таблица для хранения заданий из банк


# Таблица для хранения заданий из банка
class ExamTask(Base):
    __tablename__ = "exam_tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_number = Column(Integer, nullable=False)
    description = Column(Text, nullable=False)  
    # Формат ответа: текстовый, таблица 2 ячейки или таблица 10 ячеек
    answer_format = Column(Enum("text", "table2", "table10", name="exam_task_format"), default="text", nullable=False)
    solution_text = Column(Text, nullable=True)  # Добавил новое поле для решения
    # Правильный ответ. Если формат табличный, можно сохранить JSON-строку с массивом значений;
    # если текстовый – обычное текстовое значение.
    correct_answer = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Связь с вложениями (файлы и картинки)
    attachments = relationship("ExamTaskAttachment", back_populates="exam_task", cascade="all, delete-orphan")


from sqlalchemy import Enum as SQLAlchemyEnum
class ExamTaskAttachment(Base):
    __tablename__ = "exam_task_attachments"

    id = Column(Integer, primary_key=True, index=True)
    exam_task_id = Column(Integer, ForeignKey("exam_tasks.id"), nullable=False)
    file_path = Column(String(500), nullable=False)

    attachment_type = Column(  # заменяем file_type
        SQLAlchemyEnum(
            "task_file",          # обычный файл задания
            "task_image",         # изображение задания
            "solution_file",      # файл решения
            "solution_image",     # изображение решения
            name="exam_task_attachment_type"
        ),
        nullable=False
    )

    uploaded_at = Column(DateTime, default=datetime.utcnow)

    exam_task = relationship("ExamTask", back_populates="attachments")




class StudyGroup(Base):
    __tablename__ = "study_groups"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True)
    code = Column(String(10), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("User", back_populates="group")
    lessons = relationship("Lesson", secondary="lesson_groups", back_populates="groups")
    homeworks = relationship("Homework", secondary="homework_groups", back_populates="groups")

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
    videoLink = Column(String(500), nullable=True)
    text = Column(Text)
    files = Column(Text, nullable=True)
    image_links = Column(Text, nullable=True)
    date = Column(DateTime, default=datetime.utcnow)

    groups = relationship("StudyGroup", secondary="lesson_groups", back_populates="lessons")
    homeworks = relationship("Homework", back_populates="lesson")

class Homework(Base):
    __tablename__ = "homeworks"
    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), index=True)
    description = Column(Text)
    files = Column(Text, nullable=True)
    images = Column(Text, default="[]")
    date = Column(DateTime, default=datetime.utcnow)
    text = Column(Text)

    groups = relationship("StudyGroup", secondary="homework_groups", back_populates="homeworks")
    lesson = relationship("Lesson", back_populates="homeworks")
    status = Column(Enum("dosed", "current", name="homework_status"), default="current")

# Промежуточные таблицы для связи уроков и домашних заданий с группами
lesson_groups = Table(
    "lesson_groups",
    Base.metadata,
    Column("lesson_id", Integer, ForeignKey("lessons.id"), primary_key=True),
    Column("group_id", Integer, ForeignKey("study_groups.id"), primary_key=True)
)

homework_groups = Table(
    "homework_groups",
    Base.metadata,
    Column("homework_id", Integer, ForeignKey("homeworks.id"), primary_key=True),
    Column("group_id", Integer, ForeignKey("study_groups.id"), primary_key=True)
)

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

class HomeworkFile(Base):
    __tablename__ = "homework_files"
    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("homework_submissions.id"))
    file_path = Column(String(500))
    file_type = Column(String(255))
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    submission = relationship("HomeworkSubmission")

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


class TestSession(Base):
    __tablename__ = "test_sessions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    # Храним JSON список с ID выбранных заданий (27 заданий)
    task_ids = Column(Text, nullable=False, default="[]")
    # Для сохранения ответов, можно хранить JSON с ключами – номерами заданий
    answers = Column(Text, nullable=True, default="{}")
    expires_at = Column(DateTime, nullable=False)
    is_completed = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


def init_db():
    Base.metadata.create_all(bind=engine)


