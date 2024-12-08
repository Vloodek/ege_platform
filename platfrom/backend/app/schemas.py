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

# Схема для создания задания
class TaskCreate(BaseModel):
    name: str
    description: str
    videoLink: Optional[str] = None
    text: str
    date: datetime

# Схема для отображения задания (ответ от сервера)
class TaskResponse(BaseModel):
    id: int
    name: str
    description: str
    videoLink: Optional[str]
    text: str
    files: List[str]  # Список файлов
    date: datetime

    class Config:
        orm_mode = True

class HomeworkCreate(BaseModel):
    task_id: int  # ID задания, к которому привязана домашка
    description: str
    text: str
    files: Optional[List[str]] = []  # Пути к файлам
    date: datetime

class HomeworkResponse(BaseModel):
    id: int
    task_id: int
    description: str
    text: str
    date: datetime
    files: List[str]

    class Config:
        orm_mode = True
