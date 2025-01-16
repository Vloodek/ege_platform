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
# Настройка CORS
origins = [
    "http://localhost:8080",  # добавьте URL вашего фронтенда
    "http://192.168.1.73:8080",
    # Можно добавить другие источники, если необходимо
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # можно указать методы, если нужно
    allow_headers=["*"],  # можно указать заголовки
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
ACCESS_TOKEN_EXPIRE_MINUTES = 200 # Время жизни токена

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
    db_user = db.query(database.User).filter(database.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")
    
    hashed_password = hash_password(user.password)
    new_user = database.User(name=user.name, email=user.email, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "id": new_user.id,
        "name": new_user.name,
        "email": new_user.email
    }

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
        "role": db_user.role
    }

UPLOAD_FOLDER = "./uploads/"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Эндпоинт для создания урока (lesson)
# Внесите эти изменения в метод создания урока
@app.post("/lessons/", response_model=schemas.LessonResponse)
async def create_lesson(
    name: str = Form(...),
    description: str = Form(...),
    videoLink: Optional[str] = Form(None),
    text: str = Form(...),
    date: datetime = Form(...),
    images: Optional[List[UploadFile]] = File(None),  # Принимаем изображения
    files: Optional[List[UploadFile]] = File(None),  # Принимаем файлы
    db: Session = Depends(get_db)
):
    db_lesson = database.Lesson(
        name=name,
        description=description,
        videoLink=videoLink,
        text=text,
        date=date,
    )
    db.add(db_lesson)
    db.commit()
    db.refresh(db_lesson)

    # Создаем папку для урока, если ее нет
    lesson_folder = os.path.join(UPLOAD_FOLDER, str(db_lesson.id))
    os.makedirs(lesson_folder, exist_ok=True)

    # Папка для изображений
    images_folder = os.path.join(lesson_folder, "images")
    os.makedirs(images_folder, exist_ok=True)

    image_paths = []
    if images:
        for image in images:
            image_location = os.path.join(images_folder, image.filename)
            with open(image_location, "wb") as f:
                f.write(image.file.read())
            # Нормализуем путь для сохранения
            normalized_image_path = os.path.normpath(image_location).replace("\\", "/")
            image_paths.append(normalized_image_path)

    file_paths = []
    if files:
        for file in files:
            file_location = os.path.join(lesson_folder, file.filename)
            with open(file_location, "wb") as f:
                f.write(file.file.read())
            # Нормализуем путь для сохранения
            normalized_file_path = os.path.normpath(file_location).replace("\\", "/")
            file_paths.append(normalized_file_path)

    # Обновляем запись о уроке с путями к файлам
    db_lesson.files = ",".join(file_paths)
    db_lesson.image_links = ",".join(image_paths)  # Сохраняем пути к изображениям
    db.commit()
    db.refresh(db_lesson)

    # Преобразуем строки в списки для вывода
    db_lesson.files = db_lesson.files.split(",") if db_lesson.files else []
    db_lesson.image_links = db_lesson.image_links.split(",") if db_lesson.image_links else []
    
    return db_lesson




# Эндпоинт для получения всех уроков (lessons)
@app.get("/lessons", response_model=List[schemas.LessonResponse])
async def get_lessons(db: Session = Depends(get_db)):
    lessons = db.query(database.Lesson).all()
    for lesson in lessons:
        lesson.files = lesson.files.split(",") if lesson.files else []
        lesson.image_links = lesson.image_links.split(",") if lesson.image_links else []
    return lessons


# Эндпоинт для получения конкретного урока (lesson) по ID
# Возвращаем нормализованные данные в формате JSON
@app.get("/lessons/{lesson_id}", response_model=schemas.LessonResponse)
async def get_lesson(lesson_id: int, db: Session = Depends(get_db)):
    lesson = db.query(database.Lesson).filter(database.Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Урок не найден")
    
    # Нормализация путей с проверкой на None
    lesson.files = [os.path.normpath(f).replace("\\", "/") for f in (lesson.files or "").split(",") if f]
    lesson.image_links = [os.path.normpath(img).replace("\\", "/") for img in (lesson.image_links or "").split(",") if img]
    
    return lesson





# Эндпоинт для отдачи файлов урока (lesson)
@app.get("/lesson/{lesson_id}/uploads/{filename}")
async def get_file(lesson_id: int, filename: str):
    file_path = os.path.join('uploads', str(lesson_id), filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Файл не найден")
    return FileResponse(file_path)

@app.get("/lessons/{lesson_id}/images/{image_name}")
async def get_lesson_image(lesson_id: int, image_name: str):
    image_path = os.path.join("uploads", str(lesson_id), "images", image_name)
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(image_path)


@app.post("/homeworks/", response_model=schemas.HomeworkResponse)
async def create_homework(
    lesson_id: int = Form(...),  # Заменяем на lesson_id
    description: str = Form(...),
    text: str = Form(...),
    date: datetime = Form(...),
    files: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_db)
):
    print(f"Lesson ID: {lesson_id}, Description: {description}, Date: {date}")
    lesson = db.query(database.Lesson).filter(database.Lesson.id == lesson_id).first()
    
    if not lesson:
        raise HTTPException(status_code=404, detail="Урок не найден")

    db_homework = database.Homework(
        lesson_id=lesson_id,
        description=description,
        text=text,
        date=date,
        files="[]"  # Это временное значение, если файлов нет
    )
    db.add(db_homework)
    db.commit()
    db.refresh(db_homework)

    homework_folder = os.path.join(UPLOAD_FOLDER, str(lesson_id), "homework")
    os.makedirs(homework_folder, exist_ok=True)
    

    file_paths = []
    if files:
        for file in files:
            file_location = os.path.join(homework_folder, file.filename)
            with open(file_location, "wb") as f:
                f.write(file.file.read())
            file_paths.append(file_location)

        db_homework.files = json.dumps(file_paths)  # Сохраняем пути в формате JSON
        db.commit()
        db.refresh(db_homework)
    print(f"Lesson ID: {lesson_id}, Description: {description}, Date: {date}")
    db_homework.files = json.loads(db_homework.files) if db_homework.files else []
    return db_homework



# Получение всех домашних заданий (homeworks)
@app.get("/homeworks/", response_model=List[schemas.HomeworkResponse])
async def get_homeworks(db: Session = Depends(get_db)):
    homeworks = db.query(database.Homework).all()
    for homework in homeworks:
        homework.files = json.loads(homework.files) if homework.files else []
    return homeworks

# Получение конкретного домашнего задания (homework)
@app.get("/homeworks/{lesson_id}", response_model=List[schemas.HomeworkResponse])
async def get_homeworks_by_lesson(lesson_id: int, db: Session = Depends(get_db)):
    print(f"Получен запрос на домашки для урока с ID: {lesson_id}")
    homeworks = db.query(database.Homework).filter(database.Homework.lesson_id == lesson_id).all()
    
    if not homeworks:
        print(f"Нет домашних заданий для урока с ID {lesson_id}")
        raise HTTPException(status_code=404, detail="Домашние задания не найдены для данного урока")
    
    print(f"Найдены домашки для урока с ID {lesson_id}: {homeworks}")
    # Преобразуем файлы в список
    for homework in homeworks:
        homework.files = json.loads(homework.files) if homework.files else []
    return homeworks


from fastapi import status
@app.middleware("http")
async def check_authorization(request: Request, call_next):
    if request.method == "OPTIONS":
        return await call_next(request)  # Пропускаем OPTIONS-запросы
    if request.url.path.startswith("/uploads/"):  # Исключение для маршрутов /uploads/
        return await call_next(request)

    excluded_routes = ["/register", "/login"]  # Маршруты, где не требуется токен
    if any(request.url.path.startswith(route) for route in excluded_routes):
        return await call_next(request)  # Пропускаем проверку токена для исключенных маршрутов

    # Логируем заголовки запроса
    print(f"Запрос пришел с заголовками: {request.headers}")

    token = request.headers.get("Authorization")
    if not token:
        print("Токен не найден в заголовках")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    if not token.startswith("Bearer "):
        print(f"Некорректный токен: {token}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token format")

    try:
        payload = jwt.decode(token[7:], SECRET_KEY, algorithms=[ALGORITHM])
        user = payload.get("sub")
        if not user:
            print(f"Не найден пользователь в токене: {payload}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        request.state.user = user
        print(f"Авторизация успешна для пользователя: {user}")
    except jwt.PyJWTError as e:
        print(f"Ошибка декодирования JWT: {str(e)}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    response = await call_next(request)
    return response



