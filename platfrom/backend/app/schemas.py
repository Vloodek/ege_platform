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

    class Config:
        orm_mode = True
