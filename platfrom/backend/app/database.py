from sqlalchemy import (
    create_engine, Column, Integer, String, Text, DateTime,
    ForeignKey, Enum, Table
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

DATABASE_URL = "mysql+pymysql://root:ink-rooted-se1337@localhost:3306/ink"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Промежуточные таблицы для связей many-to-many
lesson_groups = Table(
    "lesson_groups", Base.metadata,
    Column(
        "lesson_id", Integer,
        ForeignKey("lessons.id", ondelete="CASCADE"),
        primary_key=True
    ),
    Column(
        "group_id", Integer,
        ForeignKey("study_groups.id", ondelete="CASCADE"),
        primary_key=True
    )
)

homework_groups = Table(
    "homework_groups", Base.metadata,
    Column(
        "homework_id", Integer,
        ForeignKey("homeworks.id", ondelete="CASCADE"),
        primary_key=True
    ),
    Column(
        "group_id", Integer,
        ForeignKey("study_groups.id", ondelete="CASCADE"),
        primary_key=True
    )
)


class ExamTask(Base):
    __tablename__ = "exam_tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_number = Column(Integer, nullable=False)
    description = Column(Text, nullable=False)
    answer_format = Column(
        Enum(
            "text", "table2", "table10", "tableDyn1Col", "tableDyn2Col",
            name="exam_task_format"
        ),
        default="text", nullable=False
    )
    solution_text = Column(Text, nullable=True)
    correct_answer = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    attachments = relationship(
        "ExamTaskAttachment",
        back_populates="exam_task",
        cascade="all, delete-orphan",
        passive_deletes=True
    )


class ExamTaskAttachment(Base):
    __tablename__ = "exam_task_attachments"

    id = Column(Integer, primary_key=True, index=True)
    exam_task_id = Column(
        Integer,
        ForeignKey("exam_tasks.id", ondelete="CASCADE"),
        nullable=False
    )
    file_path = Column(String(500), nullable=False)
    attachment_type = Column(
        Enum(
            "task_file",
            "task_image",
            "solution_file",
            "solution_image",
            name="exam_task_attachment_type"
        ),
        nullable=False
    )
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    exam_task = relationship(
        "ExamTask",
        back_populates="attachments"
    )


class StudyGroup(Base):
    __tablename__ = "study_groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True)
    code = Column(String(10), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("User", back_populates="group")
    lessons = relationship(
        "Lesson",
        secondary=lesson_groups,
        back_populates="groups"
    )
    homeworks = relationship(
        "Homework",
        secondary=homework_groups,
        back_populates="groups"
    )


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    email = Column(String(255), unique=True, index=True)
    password = Column(String(255))
    role = Column(String(50), default="student")  # student/teacher
    group_id = Column(
        Integer,
        ForeignKey("study_groups.id", ondelete="SET NULL"),
        nullable=True
    )
    total_points = Column(Integer, default=0, server_default="0")

    group = relationship("StudyGroup", back_populates="users")
    refresh_tokens = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True
    )


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

    groups = relationship(
        "StudyGroup",
        secondary=lesson_groups,
        back_populates="lessons"
    )
    homeworks = relationship(
        "Homework",
        back_populates="lesson",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    homework_tests = relationship(
        "HomeworkTest",
        back_populates="lesson",  # Consistent back_populates usage
        cascade="all, delete-orphan",
        passive_deletes=True
    )



class Homework(Base):
    __tablename__ = "homeworks"

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(
        Integer,
        ForeignKey("lessons.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    description = Column(Text)
    files = Column(Text, nullable=True)
    images = Column(Text, default="[]")
    date = Column(DateTime, default=datetime.utcnow)
    text = Column(Text)
    status = Column(
        Enum("dosed", "current", name="homework_status"),
        default="current"
    )

    lesson = relationship("Lesson", back_populates="homeworks")
    groups = relationship(
        "StudyGroup",
        secondary=homework_groups,
        back_populates="homeworks"
    )
    submissions = relationship(
        "HomeworkSubmission",
        back_populates="homework",
        cascade="all, delete-orphan",
        passive_deletes=True
    )


class HomeworkSubmission(Base):
    __tablename__ = "homework_submissions"

    id = Column(Integer, primary_key=True, index=True)
    homework_id = Column(
        Integer,
        ForeignKey("homeworks.id", ondelete="CASCADE"),
        nullable=False
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    student_submission_time = Column(DateTime, nullable=True)
    modified_submission_time = Column(DateTime, nullable=True)
    grade = Column(Integer, nullable=True)
    status = Column(
        Enum(
            "submitted", "graded", "response_received", "waiting",
            name="submission_status"
        ),
        default="submitted"
    )
    comment = Column(Text, nullable=True)

    homework = relationship("Homework", back_populates="submissions")
    user = relationship("User")
    files = relationship(
        "HomeworkFile",
        back_populates="submission",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    teacher_response = relationship(
        "TeacherResponse",
        back_populates="submission",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    grades = relationship(
        "Grade",
        back_populates="submission",
        cascade="all, delete-orphan",
        passive_deletes=True
    )


class HomeworkFile(Base):
    __tablename__ = "homework_files"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(
        Integer,
        ForeignKey("homework_submissions.id", ondelete="CASCADE"),
        nullable=False
    )
    file_path = Column(String(500))
    file_type = Column(String(255))
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    submission = relationship("HomeworkSubmission", back_populates="files")


class Grade(Base):
    __tablename__ = "grades"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(
        Integer,
        ForeignKey("homework_submissions.id", ondelete="CASCADE"),
        nullable=False
    )
    grade = Column(Integer)
    graded_at = Column(DateTime, default=datetime.utcnow)

    submission = relationship("HomeworkSubmission", back_populates="grades")


class TeacherResponse(Base):
    __tablename__ = "teacher_responses"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(
        Integer,
        ForeignKey("homework_submissions.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )
    teacher_comment = Column(Text, nullable=True)
    response_date = Column(DateTime, default=datetime.utcnow)

    submission = relationship("HomeworkSubmission", back_populates="teacher_response")
    files = relationship(
        "TeacherResponseFile",
        back_populates="teacher_response",
        cascade="all, delete-orphan",
        passive_deletes=True
    )


class TeacherResponseFile(Base):
    __tablename__ = "teacher_response_files"

    id = Column(Integer, primary_key=True, index=True)
    teacher_response_id = Column(
        Integer,
        ForeignKey("teacher_responses.id", ondelete="CASCADE"),
        nullable=False
    )
    file_path = Column(String(500))
    file_type = Column(String(255))
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    teacher_response = relationship("TeacherResponse", back_populates="files")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    token = Column(String(255), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="refresh_tokens")


class TestSession(Base):
    __tablename__ = "test_sessions"

    id                = Column(Integer, primary_key=True, index=True)
    user_id           = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)


    homework_test_id  = Column(Integer, ForeignKey("homework_tests.id", ondelete="CASCADE"), nullable=True)

    # JSON‑поля
    task_ids          = Column(Text,   nullable=False, default="[]")
    answers           = Column(Text,   nullable=True,  default="{}")

    expires_at        = Column(DateTime, nullable=False)
    is_completed      = Column(Integer,  default=0)
    created_at        = Column(DateTime,  default=datetime.utcnow)

    user              = relationship("User")



class HomeworkTest(Base):
    __tablename__ = "homework_tests"

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(
        Integer,
        ForeignKey("lessons.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    duration = Column(Integer, nullable=False)  # время в минутах
    tasks_meta = Column(Text, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    lesson = relationship("Lesson", back_populates="homework_tests")  # Consistent back_populates usage

    attachments = relationship(
        "HomeworkTestAttachment",
        back_populates="test",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

class HomeworkTestAttachment(Base):
    __tablename__ = "homework_test_attachments"

    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(
        Integer,
        ForeignKey("homework_tests.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    file_path = Column(String(500), nullable=False)
    attachment_type = Column(
        Enum("test_file", "test_image", name="hw_test_attachment_type"),
        nullable=False
    )
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    test = relationship("HomeworkTest", back_populates="attachments")


def init_db():
    Base.metadata.create_all(bind=engine)
