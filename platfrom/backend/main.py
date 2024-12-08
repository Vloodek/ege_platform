# main.py
from fastapi import FastAPI, Depends, HTTPException, Form, File, Request, UploadFile
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import app.database as database  # Импортируем базу данных
from app.schemas import UserRegister, UserLogin  # Импортируем модели Pydantic
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from typing import Optional
import app.schemas as schemas  # Импортируем схемы из модуля app.schemas
import os
from typing import List
from fastapi.responses import FileResponse
import json

app = FastAPI()
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
# Разрешаем CORS для всех доменов
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = (
        "script-src 'self' 'unsafe-inline';"
    )
    return response


# Инициализация базы данных
database.init_db()

# Функция для получения сессии базы данных
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Инициализация контекста для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Функция для хеширования пароля
def hash_password(password: str):
    return pwd_context.hash(password)

# Функция для проверки пароля
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Секретный ключ для подписи JWT
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Время жизни токена

# Функция для создания JWT токена
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.post("/register")
async def register(user: UserRegister, db: Session = Depends(get_db)):
    # Проверка на наличие пользователя с таким email
    db_user = db.query(database.User).filter(database.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")
    
    # Хеширование пароля перед сохранением
    hashed_password = hash_password(user.password)

    # Создание нового пользователя с хешированным паролем
    new_user = database.User(name=user.name, email=user.email, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "id": new_user.id,
        "name": new_user.name,
        "email": new_user.email
    }

# Эндпоинт для входа
@app.post("/login")
async def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(database.User).filter(database.User.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="Неверный email или пароль")

    if not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Неверный email или пароль")

    access_token = create_access_token(data={"sub": db_user.email})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "name": db_user.name,
        "role": db_user.role  # Добавляем роль в ответ
    }
# Папка для хранения файлов
UPLOAD_FOLDER = "./uploads/"

# Проверка и создание папки, если она не существует
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
# Эндпоинт для создания нового задания
@app.post("/tasks/", response_model=schemas.TaskResponse)
async def create_task(
    name: str = Form(...),
    description: str = Form(...),
    videoLink: Optional[str] = Form(None),
    text: str = Form(...),
    date: datetime = Form(...),
    files: Optional[List[UploadFile]] = File(None),  # Файлы могут быть необязательны
    db: Session = Depends(get_db)
):
    # Создаем запись задачи
    db_task = database.Task(
        name=name,
        description=description,
        videoLink=videoLink,
        text=text,
        date=date
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    # Сохраняем файлы, если они есть
    file_paths = []
    if files:
        task_folder = os.path.join(UPLOAD_FOLDER, str(db_task.id))
        os.makedirs(task_folder, exist_ok=True)
        for file in files:
            file_location = os.path.join(task_folder, file.filename)
            with open(file_location, "wb") as f:
                f.write(file.file.read())
            file_paths.append(file_location)

        # Обновляем запись с путями к файлам
        db_task.files = ",".join(file_paths)  # Здесь соединяются пути в строку
        db.commit()
        db.refresh(db_task)

    # Преобразуем строку с путями файлов обратно в список для ответа
    db_task.files = db_task.files.split(",") if db_task.files else []

    return db_task





# Эндпоинт для получения всех задач
@app.get("/tasks", response_model=List[schemas.TaskResponse])
async def get_tasks(db: Session = Depends(get_db)):
    tasks = db.query(database.Task).all()  # Извлекаем все задачи
    # Преобразуем список файлов для каждой задачи
    for task in tasks:
        task.files = task.files.split(",") if task.files else []
    return tasks




# Эндпоинт для получения конкретной задачи по ID
@app.get("/tasks/{task_id}", response_model=schemas.TaskResponse)
async def get_task(task_id: int, db: Session = Depends(get_db)):
    # Ищем задачу по ID
    task = db.query(database.Task).filter(database.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    # Преобразуем строку с путями файлов обратно в список для ответа
    task.files = task.files.split(",") if task.files else []
    return task
# Эндпоинт для отдачи файлов
@app.get("/task/{task_id}/uploads/{filename}")
async def get_file(task_id: int, filename: str):
    file_path = os.path.join('uploads', str(task_id), filename)
    
    # Проверяем, существует ли файл
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Файл не найден")
    
    # Отправляем файл
    return FileResponse(file_path)

@app.post("/homeworks/", response_model=schemas.HomeworkResponse)
async def create_homework(
    task_id: int = Form(...),
    description: str = Form(...),
    text: str = Form(...),
    date: datetime = Form(...),
    files: Optional[List[UploadFile]] = File(None),  # Файлы могут быть необязательны
    db: Session = Depends(get_db)
):
    # Создаем запись для домашнего задания
    db_homework = database.Homework(
        task_id=task_id,
        description=description,
        text=text,
        date=date,
        files="[]"  # Инициализируем пустой список файлов в строковом формате
    )
    db.add(db_homework)
    db.commit()
    db.refresh(db_homework)

    # Сохраняем файлы, если они есть
    if files:
        homework_folder = os.path.join(UPLOAD_FOLDER, str(db_homework.id))
        os.makedirs(homework_folder, exist_ok=True)
        file_paths = []
        for file in files:
            file_location = os.path.join(homework_folder, file.filename)
            with open(file_location, "wb") as f:
                f.write(file.file.read())
            file_paths.append(file_location)

        # Сохраняем список путей к файлам в JSON-формате
        db_homework.files = json.dumps(file_paths)
        db.commit()
        db.refresh(db_homework)

    # Преобразуем строку JSON в список для возврата
    db_homework.files = json.loads(db_homework.files) if db_homework.files else []
    return db_homework



# Получение всех домашних заданий
@app.get("/homeworks/", response_model=List[schemas.HomeworkResponse])
async def get_homeworks(db: Session = Depends(get_db)):
    homeworks = db.query(database.Homework).all()
    for homework in homeworks:
        # Преобразуем JSON-строку в список для корректного ответа
        homework.files = json.loads(homework.files) if homework.files else []
    return homeworks

# Получение конкретного домашнего задания
@app.get("/homeworks/{homework_id}", response_model=schemas.HomeworkResponse)
async def get_homework(homework_id: int, db: Session = Depends(get_db)):
    homework = db.query(database.Homework).filter(database.Homework.id == homework_id).first()
    if not homework:
        raise HTTPException(status_code=404, detail="Домашнее задание не найдено")
    # Преобразуем JSON-строку в список для корректного ответа
    homework.files = json.loads(homework.files) if homework.files else []
    return homework

