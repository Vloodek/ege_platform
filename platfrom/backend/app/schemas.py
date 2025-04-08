from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

# Схема для регистрации пользователя
class UserRegister(BaseModel):
    name: str
    email: str
    password: str

# Схема для входа пользователя
class UserLogin(BaseModel):
    email: str
    password: str

# Схема для создания урока
class LessonCreate(BaseModel):
    name: str
    description: str
    videoLink: Optional[str] = None
    text: str
    date: datetime
    files: Optional[List[str]] = []  # Пути к прикрепленным файлам
    images: Optional[List[str]] = []  # Пути к загруженным изображениям

# Схема для отображения урока (ответ от сервера)
class LessonResponse(BaseModel):
    id: int
    name: str
    description: str
    videoLink: Optional[str] = None
    text: str
    date: datetime
    files: List[str] = []  # Пути к файлам
    image_links: List[str] = []  # Пути к изображениям

    class Config:
        orm_mode = True

class HomeworkCreate(BaseModel):
    lesson_id: int  # ID урока, к которому привязана домашка
    description: str
    text: str
    files: Optional[List[str]] = []  # Пути к файлам
    date: datetime

class HomeworkResponse(BaseModel):
    id: int
    lesson_id: int
    description: str
    text: str
    date: datetime
    files: List[str]
    images: List[str] = []  # Добавляем поле images!

    class Config:
        orm_mode = True

# Отправка домашнего задания
class HomeworkSubmissionCreate(BaseModel):
    homework_id: int
    user_id: int
    comment: Optional[str] = None  # Комментарий или текст ответа
    files: Optional[List[str]] = []  # Пути к прикрепленным файлам


# Ответ с данными о домашке
class HomeworkSubmissionResponse(BaseModel):
    id: int
    homework_id: int
    user_id: int
    grade: Optional[int]
    status: str

    class Config:
        orm_mode = True

# Файлы, прикрепленные к отправке
class HomeworkFileCreate(BaseModel):
    submission_id: int
    file_path: str
    file_type: str

class HomeworkFileResponse(BaseModel):
    id: int
    submission_id: int
    file_path: str
    file_type: str
    uploaded_at: datetime

    class Config:
        orm_mode = True

# Оценки
class GradeCreate(BaseModel):
    submission_id: int
    grade: int

class GroupCreate(BaseModel):
    name: str

class GroupResponse(BaseModel):
    id: int
    name: str
    code: str

    class Config:
        orm_mode = True

class JoinGroup(BaseModel):
    code: str

class JoinGroupRequest(BaseModel):
    user_id: int

class HomeworkUpdate(BaseModel):
    lesson_id: Optional[int]
    description: Optional[str]
    text: Optional[str]
    date: Optional[str]
    images: Optional[List[str]]
    files: Optional[List[str]]

    class Config:
        from_attributes = True  # Убедись, что включен режим атрибутов для ORM

class HomeworkListItem(BaseModel):
    id: int
    lesson_id: int
    description: str
    date: datetime

# Схема для отображения пользователя (ответ от сервера)
class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    group_id: Optional[int] = None  # ID группы, если есть
    total_points: int

    class Config:
        orm_mode = True

class ExamTaskAttachmentResponse(BaseModel):
    id: int
    exam_task_id: int
    file_path: str
    attachment_type: str  # Было file_type → attachment_type
    uploaded_at: datetime

    class Config:
        orm_mode = True

class ExamTaskResponse(BaseModel):
    id: int
    task_number: int
    description: str
    answer_format: str
    correct_answer: Optional[str]
    created_at: datetime
    updated_at: datetime
    attachments: List[ExamTaskAttachmentResponse]  # Используем исправленную схему

    class Config:
        orm_mode = True

from typing import Dict
class ExamTaskCountByTypeResponse(BaseModel):
    counts: Dict[int, int]  # Ключ - тип задания (task_number), значение - количество

    class Config:
        orm_mode = True

