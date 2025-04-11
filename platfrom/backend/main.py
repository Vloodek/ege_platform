# main.py
import sys
print(sys.path)

from fastapi import FastAPI, Depends, HTTPException, Form, File, Request, UploadFile
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import app.database as database  # Импортируем базу данных
from app.schemas import UserRegister, UserLogin,JoinGroupRequest  # Импортируем модели Pydantic
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from typing import Optional
import app.schemas as schemas  # Импортируем схемы из модуля app.schemas
import os
from typing import List, Dict
from fastapi.responses import FileResponse
import json
from app.database import init_db  # Импортируем функцию инициализации БД
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # Указываем разрешенные источники
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

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
ACCESS_TOKEN_EXPIRE_MINUTES = 200
REFRESH_TOKEN_EXPIRE_DAYS = 1  # Время жизни рефреш-токена

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
    # Проверка, что пользователь с таким email уже существует
    db_user = db.query(database.User).filter(database.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")
    
    # Хэширование пароля
    hashed_password = hash_password(user.password)
    new_user = database.User(name=user.name, email=user.email, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Создание access_token
    access_token = create_access_token(data={"sub": new_user.email})
    
    # Создание refresh_token и сохранение в базе данных
    refresh_token = create_refresh_token(new_user.id, db)

    # Формирование ответа
    response = JSONResponse(content={
        "access_token": access_token,
        "token_type": "bearer",
        "name": new_user.name,
        "role": new_user.role,
        "id": new_user.id,
        "group_id": new_user.group_id
    })
    
    # Установка рефреш-токена в куки
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,  
        samesite="Strict",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60  # Время жизни куки в секундах
    )

    # Добавление CORS заголовков
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:8080"  # Разрешаем доступ только с клиента на 8080 порту
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Credentials"] = "true"

    return response

import secrets

def create_refresh_token(user_id: int, db: Session):
    expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    print(expires_at,'DDDDDDDDDDDDDDDDDD')
    print(datetime.utcnow())
    print(timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    refresh_token = secrets.token_urlsafe(32)  # Генерация случайного токена
    db_refresh_token = database.RefreshToken(
        user_id=user_id,
        token=refresh_token,
        expires_at=expires_at,
    )
    db.add(db_refresh_token)
    db.commit()
    db.refresh(db_refresh_token)
    return refresh_token

@app.post("/login")
async def login(user: UserLogin, request: Request, db: Session = Depends(get_db)):
    db_user = db.query(database.User).filter(database.User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Неверный email или пароль")

    access_token = create_access_token(data={"sub": db_user.email})
    refresh_token = create_refresh_token(db_user.id, db)

    # Если у пользователя установлен group_id, получаем имя группы
    group_name = None
    if db_user.group_id:
        group = db.query(database.StudyGroup).filter(database.StudyGroup.id == db_user.group_id).first()
        if group:
            group_name = group.name

    response = JSONResponse(content={
        "access_token": access_token,
        "token_type": "bearer",
        "name": db_user.name,
        "role": db_user.role,
        "id": db_user.id,
        "group_id": db_user.group_id,
        "group_name": group_name  # Добавлено имя группы
    })

    # Установка куки с рефреш-токеном
    response.set_cookie(
        key="refresh_token", 
        value=refresh_token, 
        httponly=True,  # Запрещает доступ к куки через JavaScript
        samesite="Strict",  # Ограничение для куки по сайтам
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60  # Время жизни куки в секундах
    )

    response.headers["Access-Control-Allow-Origin"] = "http://localhost:8080"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Credentials"] = "true"

    return response


@app.post("/refresh-token")
async def refresh_token(request: Request, db: Session = Depends(get_db)):
    # Получаем refresh_token из куки
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        print("Refresh token not found in cookies")
        raise HTTPException(status_code=401, detail="Рефреш-токен отсутствует")

    print(f"Received refresh token: {refresh_token}")

    

    db_refresh_token = db.query(database.RefreshToken).filter_by(token=refresh_token).first()
    if not db_refresh_token:
        print("Refresh token not found in database")
        raise HTTPException(status_code=401, detail="Неверный рефреш-токен")

    # Проверка срока действия рефреш-токена
    if db_refresh_token.expires_at < datetime.utcnow():
        print(f"Refresh token expired: {db_refresh_token.expires_at}")
        raise HTTPException(status_code=401, detail="Рефреш-токен истек")

    

    # Удаляем старый рефреш-токен
    db.delete(db_refresh_token)
    db.commit()

    # Создаем новый access и refresh токены
    user = db.query(database.User).filter_by(id=db_refresh_token.user_id).first()
    access_token = create_access_token(data={"sub": user.email})
    new_refresh_token = create_refresh_token(user.id, db)

    response = JSONResponse(content={"access_token": access_token})
    response.set_cookie(
        key="refresh_token", 
        value=new_refresh_token, 
        httponly=True, 
        samesite="Strict",  # Ограничение для куки по сайтам
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60  # Время жизни куки в секундах
    )
    return response


UPLOAD_FOLDER = "./uploads/"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Эндпоинт для создания урока (lesson)
@app.post("/lessons/", response_model=schemas.LessonResponse)
async def create_lesson(
    name: str = Form(...),
    description: str = Form(...),
    videoLink: Optional[str] = Form(None),
    text: str = Form(...),
    date: datetime = Form(...),
    group_id: int = Form(...),  # Добавляем выбор группы
    images: Optional[List[UploadFile]] = File(None),
    files: Optional[List[UploadFile]] = File(None),
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

    # Получаем группу по group_id
    group = db.query(database.StudyGroup).filter(database.StudyGroup.id == group_id).first()
    if group:
        # Добавляем группу в список групп урока
        db_lesson.groups.append(group)
        db.commit()
        db.refresh(db_lesson)

    lesson_folder = os.path.join(UPLOAD_FOLDER, str(db_lesson.id))
    os.makedirs(lesson_folder, exist_ok=True)

    images_folder = os.path.join(lesson_folder, "images")
    os.makedirs(images_folder, exist_ok=True)

    image_paths = []
    if images:
        for image in images:
            image_location = os.path.join(images_folder, image.filename)
            with open(image_location, "wb") as f:
                f.write(image.file.read())
            normalized_image_path = os.path.normpath(image_location).replace("\\", "/")
            image_paths.append(normalized_image_path)

    file_paths = []
    if files:
        for file in files:
            file_location = os.path.join(lesson_folder, file.filename)
            with open(file_location, "wb") as f:
                f.write(file.file.read())
            normalized_file_path = os.path.normpath(file_location).replace("\\", "/")
            file_paths.append(normalized_file_path)

    db_lesson.files = ",".join(file_paths)
    db_lesson.image_links = ",".join(image_paths)
    db.commit()
    db.refresh(db_lesson)

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
    lesson_id: int = Form(...),
    description: str = Form(...),
    text: str = Form(...),
    date: datetime = Form(...),
    files: Optional[List[UploadFile]] = File(None),
    images: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_db)
):
    lesson = db.query(database.Lesson).filter(database.Lesson.id == lesson_id).first()
    
    if not lesson:
        raise HTTPException(status_code=404, detail="Урок не найден")

    db_homework = database.Homework(
        lesson_id=lesson_id,
        description=description,
        text=text,
        date=date,
        files="[]",
        images="[]",
        
    )
    db.add(db_homework)
    db.commit()
    db.refresh(db_homework)

    # Привязываем домашнее задание к группам, к которым принадлежит урок
    # Если урок может принадлежать сразу нескольким группам:
    for group in lesson.groups:
        db_homework.groups.append(group)
    db.commit()
    db.refresh(db_homework)

    homework_folder = os.path.join(UPLOAD_FOLDER, str(lesson_id), "homework")
    os.makedirs(homework_folder, exist_ok=True)

    file_paths = []
    image_paths = []

    if files:
        for file in files:
            file_location = os.path.join(homework_folder, file.filename)
            with open(file_location, "wb") as f:
                f.write(file.file.read())
            file_paths.append(file_location)

    if images:
        for image in images:
            image_location = os.path.join(homework_folder, image.filename)
            with open(image_location, "wb") as f:
                f.write(image.file.read())
            image_paths.append(image_location)

    db_homework.files = json.dumps(file_paths)
    db_homework.images = json.dumps(image_paths)  # Сохраняем пути в формате JSON

    db.commit()
    db.refresh(db_homework)

    db_homework.files = json.loads(db_homework.files) if db_homework.files else []
    db_homework.images = json.loads(db_homework.images) if db_homework.images else []

    return db_homework




@app.get("/homeworks/", response_model=List[schemas.HomeworkResponse])
async def get_homeworks(db: Session = Depends(get_db)):
    homeworks = db.query(database.Homework).all()
    for homework in homeworks:
        homework.files = json.loads(homework.files) if homework.files else []
        # Убираем обработку images, если она не нужна
        homework.images = []  # Можно просто очистить список или убрать строку
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

    # Преобразуем файлы и изображения в списки
    for homework in homeworks:
        homework.files = json.loads(homework.files) if homework.files else []
        homework.images = json.loads(homework.images) if homework.images else []  # Добавляем обработку images
    
    return homeworks



from fastapi import status
from fastapi.responses import JSONResponse
@app.middleware("http")
async def check_authorization(request: Request, call_next):
    if request.method == "OPTIONS":
        return await call_next(request)  # Пропускаем OPTIONS-запросы
    print(f"Обрабатываемый путь запроса: {request.url.path}")

    if "/uploads/" in request.url.path or request.url.path == "/favicon.ico":
        return await call_next(request)


    excluded_routes = ["/register", "/login", "/refresh-token", "/docs","/openapi.json","/sse/timer"]  # Маршруты, где не требуется токен
    if any(request.url.path.startswith(route) for route in excluded_routes):
        return await call_next(request)  # Пропускаем проверку токена для исключенных маршрутов

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
        return JSONResponse(
    status_code=401,
    content={"detail": "Invalid token"},
    headers={
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Credentials": "true"
    }
)
        
        
    
    response = await call_next(request)
    return response


@app.post("/submit_homework", response_model=schemas.HomeworkSubmissionResponse)
async def submit_homework(
    homework_id: int = Form(...),
    user_id: int = Form(...),
    comment: Optional[str] = Form(None),
    student_submission_time: Optional[str] = Form(None),
    files: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_db)
):
    # Определяем клиентское время
    if student_submission_time:
        try:
            client_time = datetime.fromisoformat(student_submission_time)
        except Exception:
            client_time = datetime.utcnow()
    else:
        client_time = datetime.utcnow()

    # Создаем запись отклика
    submission = database.HomeworkSubmission(
        homework_id=homework_id,
        user_id=user_id,
        comment=comment,
        student_submission_time=datetime.utcnow()
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)

    # Получаем домашнее задание, чтобы определить lesson_id
    homework_obj = db.query(database.Homework).filter(database.Homework.id == homework_id).first()
    if not homework_obj:
        raise HTTPException(status_code=404, detail="Домашнее задание не найдено")
    lesson_id = homework_obj.lesson_id

    # Формируем путь для хранения файлов
    base_homework_folder = os.path.normpath(os.path.join(UPLOAD_FOLDER, str(lesson_id), "homework"))
    os.makedirs(base_homework_folder, exist_ok=True)

    submission_folder = os.path.normpath(os.path.join(base_homework_folder, str(user_id)))
    os.makedirs(submission_folder, exist_ok=True)

    # Сохраняем файлы отклика
    if files:
        for file in files:
            file_location = os.path.normpath(os.path.join(submission_folder, file.filename))
            with open(file_location, "wb") as f:
                f.write(file.file.read())

            db_file = database.HomeworkFile(
                submission_id=submission.id,
                file_path=file_location,
                file_type=file.content_type
            )
            db.add(db_file)

        db.commit()

    return submission


@app.get("/homeworks/{homework_id}/submission")
async def get_submission(homework_id: int, user_id: int, db: Session = Depends(get_db)):
    """
    Возвращает отправленный ответ на домашнее задание для конкретного пользователя.
    """
    submission = (
        db.query(database.HomeworkSubmission)
        .filter(
            database.HomeworkSubmission.homework_id == homework_id,
            database.HomeworkSubmission.user_id == user_id
        )
        .first()
    )
    if not submission:
        raise HTTPException(status_code=404, detail="Ответ не найден")
    
    # Получаем список файлов, прикрепленных к ответу
    submission_files = db.query(database.HomeworkFile).filter(
        database.HomeworkFile.submission_id == submission.id
    ).all()
    file_paths = [file.file_path for file in submission_files]
    
    # Получаем оценку из таблицы Grade
    grade_obj = db.query(database.Grade).filter(
        database.Grade.submission_id == submission.id
    ).first()
    teacher_grade = grade_obj.grade if grade_obj else None

    return {
        "id": submission.id,
        "homework_id": submission.homework_id,
        "user_id": submission.user_id,
        "user_name": submission.user.name,
        "student_submission_time": submission.student_submission_time.isoformat(),
        "grade": teacher_grade,
        "status": submission.status,
        "comment": submission.comment,
        "modified_submission_time": submission.modified_submission_time.isoformat() if submission.modified_submission_time else None,
        "files": file_paths
    }





@app.put("/update_submission/{submission_id}")
async def update_submission(
    submission_id: int,
    comment: str = Form(...),
    files: Optional[List[UploadFile]] = File(None),
    files_to_delete: str = Form("[]"),  # JSON-список файлов для удаления
    db: Session = Depends(get_db)
):
    # Ищем существующий ответ по submission_id
    submission = db.query(database.HomeworkSubmission).filter(database.HomeworkSubmission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Ответ не найден")

    # Обновляем комментарий
    submission.comment = comment

    # Устанавливаем время модификации на сервере (не от клиента)
    submission.modified_submission_time = datetime.utcnow()

    # Если время отправки еще не задано, то назначаем его (оно устанавливается только сервером)
    if not submission.student_submission_time:
        submission.student_submission_time = datetime.utcnow()

    # Устанавливаем статус как "submitted", так как отклик обновляется
    submission.status = "submitted"

    # Удаление файлов
    files_to_delete = json.loads(files_to_delete)  # Преобразуем JSON-строку в список
    if files_to_delete:
        for file_path in files_to_delete:
            full_path = os.path.normpath(file_path)

            # Удаляем физический файл
            if os.path.exists(full_path):
                os.remove(full_path)

            # Удаляем запись о файле из БД
            file_record = db.query(database.HomeworkFile).filter(database.HomeworkFile.file_path == full_path).first()
            if file_record:
                db.delete(file_record)

    # Если передаются новые файлы, сохраняем их
    if files:
        homework_obj = db.query(database.Homework).filter(database.Homework.id == submission.homework_id).first()
        lesson_id = homework_obj.lesson_id if homework_obj else "default"
        submission_folder = os.path.normpath(os.path.join("uploads", str(lesson_id), "homework", str(submission.user_id)))
        os.makedirs(submission_folder, exist_ok=True)

        for file in files:
            file_location = os.path.normpath(os.path.join(submission_folder, file.filename))
            with open(file_location, "wb") as f:
                f.write(file.file.read())

            new_file = database.HomeworkFile(
                submission_id=submission.id,
                file_path=file_location,
                file_type=file.content_type
            )
            db.add(new_file)

    db.commit()
    db.refresh(submission)

    return {"message": "Ответ обновлен", "deleted_files": files_to_delete, "submission": submission}



@app.post("/grade_homework")
async def grade_homework(
    submission_id: int = Form(...),
    grade: int = Form(...),
    db: Session = Depends(get_db)
):
    # Получаем отклик
    submission = db.query(database.HomeworkSubmission)\
                   .filter(database.HomeworkSubmission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    submission.grade = grade
    submission.status = "graded"
    
    # Создаем запись в таблице Grade
    db_grade = database.Grade(submission_id=submission.id, grade=grade)
    db.add(db_grade)
    
    # Обновляем total_points пользователя
    user = db.query(database.User).filter(database.User.id == submission.user_id).first()
    if user:
        # Если total_points ещё не инициализировано, считаем его равным 0
        user.total_points = (user.total_points or 0) + grade
    
    db.commit()
    
    return {"message": "Grade assigned successfully"}



import random
import string

def generate_group_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

@app.post("/groups/", response_model=schemas.GroupResponse)
async def create_group(group: schemas.GroupCreate, db: Session = Depends(get_db)):
    group_code = generate_group_code()
    db_group = database.StudyGroup(name=group.name, code=group_code)  # Заменено на StudyGroup
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group

from fastapi import Body

@app.post("/groups/join/{group_code}")
async def join_group(
    request: Request, 
    group_code: str, 
    body: JoinGroupRequest = Body(...), 
    db: Session = Depends(get_db)
):
    group = db.query(database.StudyGroup).filter(database.StudyGroup.code == group_code).first()
    if not group:
        return JSONResponse(status_code=404, content={"message": "Группа не найдена"})
    
    user = db.query(database.User).filter(database.User.id == body.user_id).first()
    if not user:
        return JSONResponse(status_code=404, content={"message": "Пользователь не найден"})

    user.group_id = group.id
    db.commit()

    return {
        "message": f"Пользователь {user.name} успешно добавлен в группу {group.name}",
        "group_id": group.id,
        "group_name": group.name
    }



# Список всех групп
@app.get("/groups/", response_model=List[schemas.GroupResponse])
async def get_groups(db: Session = Depends(get_db)):
    groups = db.query(database.StudyGroup).all()  
    return groups

# Эндпоинт для получения всех пользователей в группе
@app.get("/groups/{group_id}/users", response_model=List[schemas.UserResponse])
async def get_group_users(group_id: int, db: Session = Depends(get_db)):
    group = db.query(database.StudyGroup).filter(database.StudyGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    users = db.query(database.User).filter(database.User.group_id == group.id).all()
    return users

@app.get("/homework/{homework_id}", response_model=schemas.HomeworkResponse)
async def get_homework(homework_id: int, db: Session = Depends(get_db)):
    homework = db.query(database.Homework).filter(database.Homework.id == homework_id).first()
    if not homework:
        raise HTTPException(status_code=404, detail="Homework not found")
    # Если файлы сохранены как JSON, преобразуем их обратно в список
    if homework.files:
        homework.files = json.loads(homework.files)
    # Если ссылки на изображения сохранены как строка, можно их преобразовать (если нужно)
    if homework.images:
        homework.images = json.loads(homework.images)
    return homework


@app.put("/homeworks/{homework_id}", response_model=schemas.HomeworkResponse)
async def update_homework(
    homework_id: int,
    lesson_id: int = Form(...),
    description: str = Form(...),
    text: str = Form(...),
    date: datetime = Form(...),
    files: Optional[List[UploadFile]] = File(None),
    images: Optional[List[UploadFile]] = File(None),
    existing_files: Optional[str] = Form("[]"),
    existing_images: Optional[str] = Form("[]"),
    db: Session = Depends(get_db)
):
    # Проверяем, существует ли домашка
    db_homework = db.query(database.Homework).filter(database.Homework.id == homework_id).first()
    if not db_homework:
        raise HTTPException(status_code=404, detail="Домашнее задание не найдено")
    
    homework_folder = os.path.join(UPLOAD_FOLDER, str(lesson_id), "homework")
    os.makedirs(homework_folder, exist_ok=True)
    
    # Загружаем существующие файлы и изображения
    existing_files = json.loads(existing_files)
    existing_images = json.loads(existing_images)
    
    # Удаляем старые файлы, которых нет в existing_files
    current_files = json.loads(db_homework.files) if db_homework.files else []
    for file in current_files:
        if file not in existing_files and os.path.exists(file):
            os.remove(file)
    
    # Удаляем старые изображения, которых нет в existing_images
    current_images = json.loads(db_homework.images) if db_homework.images else []
    for image in current_images:
        if image not in existing_images and os.path.exists(image):
            os.remove(image)
    
    file_paths = existing_files[:]
    image_paths = existing_images[:]

    # Загружаем новые файлы
    if files:
        for file in files:
            file_location = os.path.join(homework_folder, file.filename)
            with open(file_location, "wb") as f:
                f.write(file.file.read())
            file_paths.append(file_location)
    
    if images:
        for image in images:
            image_location = os.path.join(homework_folder, image.filename)
            with open(image_location, "wb") as f:
                f.write(image.file.read())
            image_paths.append(image_location)
    
    # Обновляем данные в базе
    db_homework.lesson_id = lesson_id
    db_homework.description = description
    db_homework.text = text
    db_homework.date = date
    db_homework.files = json.dumps(file_paths)
    db_homework.images = json.dumps(image_paths)
    
    db.commit()
    db.refresh(db_homework)
    
    db_homework.files = json.loads(db_homework.files) if db_homework.files else []
    db_homework.images = json.loads(db_homework.images) if db_homework.images else []
    
    return db_homework


from fastapi import Query

@app.get("/api/homework/{homework_id}/submissions")
async def get_submissions(
    homework_id: int,
    group: int = Query(None),
    db: Session = Depends(get_db)
):
    # Получаем домашнее задание по ID
    homework = db.query(database.Homework).filter(database.Homework.id == homework_id).first()
    if not homework:
        raise HTTPException(status_code=404, detail="Homework not found")

    # Базовый запрос на отклики для домашнего задания
    submissions_query = db.query(database.HomeworkSubmission).filter(
        database.HomeworkSubmission.homework_id == homework_id
    )

    # Если передан параметр group, объединяем с таблицей пользователей и фильтруем по группе
    if group is not None:
        submissions_query = submissions_query.join(database.User).filter(database.User.group_id == group)

    submissions = submissions_query.all()

    result = []
    for submission in submissions:
        user = db.query(database.User).filter(database.User.id == submission.user_id).first()
        if user:
            result.append({
                "id": submission.id,       # id отклика
                "user_id": user.id,        # id пользователя
                "name": user.name,
                "email": user.email,
                "status": submission.status,
                "submission_date": submission.student_submission_time.isoformat() if submission.student_submission_time else None,
                "client_submission_time": submission.modified_submission_time.isoformat() if submission.modified_submission_time else None,
            })

    return result


@app.put("/update_teacher_response/{submission_id}")
async def update_teacher_response(
    submission_id: int,
    teacher_comment: str = Form(...),
    teacher_grade: str = Form(""),  # Принимаем как строку, чтобы пустое значение не вызывало ошибок
    files: Optional[List[UploadFile]] = File(None),
    files_to_delete: str = Form("[]"),  # JSON-строка со списком файлов для удаления
    db: Session = Depends(get_db)
):
    print(f"teacher_grade: {teacher_grade}, teacher_comment: {teacher_comment}, files: {files}")

    # Получаем отклик
    submission = db.query(database.HomeworkSubmission)\
                   .filter(database.HomeworkSubmission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Отклик не найден")
    
    # Получаем или создаем ответ преподавателя
    teacher_response = db.query(database.TeacherResponse)\
                         .filter(database.TeacherResponse.submission_id == submission_id).first()
    
    if teacher_response is None:
        teacher_response = database.TeacherResponse(
            submission_id=submission_id,
            teacher_comment=teacher_comment,
            response_date=datetime.utcnow()
        )
        db.add(teacher_response)
        db.commit()
        db.refresh(teacher_response)
    else:
        teacher_response.teacher_comment = teacher_comment
        teacher_response.response_date = datetime.utcnow()
    
    # Обработка удаления файлов
    try:
        files_to_delete_list = json.loads(files_to_delete)
    except Exception:
        raise HTTPException(status_code=400, detail="Неверный формат files_to_delete")
    
    if files_to_delete_list:
        for file_path in files_to_delete_list:
            full_path = file_path.replace("/", "\\")
            print(f"Пытаемся удалить файл: {full_path}")
            if os.path.exists(full_path):
                os.remove(full_path)
                print(f"Файл удалён: {full_path}")
            else:
                print(f"Файл не найден на диске: {full_path}")
            file_record = db.query(database.TeacherResponseFile).filter(
                database.TeacherResponseFile.file_path == full_path,
                database.TeacherResponseFile.teacher_response_id == teacher_response.id
            ).first()
            if file_record:
                db.delete(file_record)
                print(f"Запись о файле с путём {full_path} удалена из БД")
            else:
                print(f"Запись о файле с путём {full_path} не найдена в БД")
    
    # Обработка новых файлов
    if files:
        teacher_folder = os.path.join("uploads", str(submission.homework_id), "homework", str(submission.user_id), "teacher_answer")
        os.makedirs(teacher_folder, exist_ok=True)
        for file in files:
            file_location = os.path.join(teacher_folder, file.filename)
            with open(file_location, "wb") as f:
                f.write(file.file.read())
            new_file = database.TeacherResponseFile(
                teacher_response_id=teacher_response.id,
                file_path=file_location,
                file_type=file.content_type
            )
            db.add(new_file)
    
    # Обработка оценки – обновляем запись в таблице Grade и корректируем total_points
    grade_obj = db.query(database.Grade)\
                  .filter(database.Grade.submission_id == submission_id).first()
    # Определяем старую оценку (если есть); если оценки не было, считаем old_grade = 0
    old_grade = grade_obj.grade if (grade_obj is not None and grade_obj.grade is not None) else 0
    print("DDDDDDDDDDDDDDDDDAS")
    print(old_grade)
    if teacher_grade.strip() != "":
        try:
            parsed_grade = int(teacher_grade)
        except ValueError:
            raise HTTPException(status_code=400, detail="Оценка должна быть целым числом")
        diff = parsed_grade - old_grade  # разница между новой и старой оценкой
        if grade_obj is None:
            grade_obj = database.Grade(
                submission_id=submission_id,
                grade=parsed_grade,
                graded_at=datetime.utcnow()
            )
            db.add(grade_obj)
        else:
            grade_obj.grade = parsed_grade
            grade_obj.graded_at = datetime.utcnow()
        submission.status = "graded"
    else:
        diff = -old_grade
        if grade_obj is None:
            grade_obj = database.Grade(
                submission_id=submission_id,
                grade=None,
                graded_at=datetime.utcnow()
            )
            db.add(grade_obj)
        else:
            grade_obj.grade = None
            grade_obj.graded_at = datetime.utcnow()
        submission.status = "response_received"
    
    # Отладка: выводим diff и текущее значение total_points
    user = db.query(database.User).filter(database.User.id == submission.user_id).first()
    if user:
        current_total = user.total_points or 0
        new_total = current_total + diff
        print(f"Updating user {user.id}: total_points {current_total} + diff {diff} = {new_total}")
        user.total_points = new_total
        db.flush()  # явно отправляем изменения в базу (без коммита)
    
    db.commit()
    db.refresh(teacher_response)
    
    response_data = {
        "teacher_comment": teacher_response.teacher_comment,
        "response_date": teacher_response.response_date.isoformat(),
        "teacher_grade": grade_obj.grade if grade_obj else None,
        "files": [
            {"file_path": file.file_path, "file_name": os.path.basename(file.file_path)}
            for file in teacher_response.files
        ]
    }
    
    return {
        "message": "Ответ преподавателя обновлён",
        "teacher_response": response_data
    }


@app.get("/teacher_response/{submission_id}")
async def get_teacher_response(submission_id: int, db: Session = Depends(get_db)):
    # Получаем отклик студента
    submission = db.query(database.HomeworkSubmission).filter(
        database.HomeworkSubmission.id == submission_id
    ).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Отклик не найден")
    
    # Получаем ответ преподавателя (без оценки)
    teacher_response = db.query(database.TeacherResponse).filter(
        database.TeacherResponse.submission_id == submission_id
    ).first()
    if not teacher_response:
        raise HTTPException(status_code=404, detail="Ответ преподавателя не найден")
    
    # Получаем оценку из таблицы Grade
    grade_obj = db.query(database.Grade).filter(
        database.Grade.submission_id == submission_id
    ).first()
    teacher_grade = grade_obj.grade if grade_obj else None

    # Получаем список файлов, прикреплённых преподавателем
    teacher_files = db.query(database.TeacherResponseFile).filter(
        database.TeacherResponseFile.teacher_response_id == teacher_response.id
    ).all()

    response_data = {
        "teacher_comment": teacher_response.teacher_comment,
        "teacher_grade": teacher_grade,
        "files": [
            {"file_path": file.file_path, "file_name": os.path.basename(file.file_path)}
            for file in teacher_files
        ]
    }

    return response_data



@app.get("/homeworks/{homework_id}/feedback")
def get_teacher_feedback(homework_id: int, user_id: int, db: Session = Depends(get_db)):
    feedback = db.query(database.teacher_responses).filter_by(homework_id=homework_id, user_id=user_id).first()
    if not feedback:
        return {"comment": None, "grade": None}
    return {"comment": feedback.comment, "grade": feedback.grade}


@app.get("/homeworks/by_lesson/{lesson_id}/id")
async def get_homework_id_by_lesson(lesson_id: int, db: Session = Depends(get_db)):
    homework_obj = db.query(database.Homework).filter(database.Homework.lesson_id == lesson_id).first()
    if not homework_obj:
        raise HTTPException(status_code=404, detail="Домашнее задание не найдено")
    return {"id": homework_obj.id}


@app.post("/exam_tasks/", response_model=schemas.ExamTaskResponse)
def create_exam_task(
    task_number: int = Form(...),
    description: str = Form(...),
    solution_text: str = Form(""),
    answer_format: str = Form(...),
    correct_answer: str = Form(...),
    taskFiles: list[UploadFile] = File(default=[]),
    taskImages: list[UploadFile] = File(default=[]),
    solution_files: list[UploadFile] = File(default=[]),
    solution_images: list[UploadFile] = File(default=[]),
    db: Session = Depends(get_db),
):
    # Создаем задание в БД
    task = database.ExamTask(
        task_number=task_number,
        description=description,
        solution_text=solution_text,
        answer_format=answer_format,
        correct_answer=correct_answer,
    )
    db.add(task)
    db.commit()   # фиксируем задание, чтобы получить task.id
    db.refresh(task)

    # Определяем путь для хранения файлов: ./uploads/tasks_bank/{task_number}/{task.id}
    base_path = f"./uploads/tasks_bank/{task_number}/{task.id}"
    os.makedirs(os.path.join(base_path, "files"), exist_ok=True)
    os.makedirs(os.path.join(base_path, "images"), exist_ok=True)

    # Функция сохранения файлов и записи в БД
    def save_files(files: list[UploadFile], folder: str, file_type: str):
        for file in files:
            # Обязательно сбрасываем указатель, если файл уже был прочитан
            file.file.seek(0)
            content = file.file.read()
            save_path = os.path.join(base_path, folder, file.filename)
            with open(save_path, "wb") as f:
                f.write(content)
            # Формируем запись вложения
            attachment = database.ExamTaskAttachment(
                exam_task_id=task.id,
                file_path=save_path.replace("\\", "/"),
                attachment_type=file_type,
            )
            db.add(attachment)
            # Если связь attachment определена у ExamTask, можно добавить в список:
            if not hasattr(task, "attachments") or task.attachments is None:
                task.attachments = []
            task.attachments.append(attachment)
            db.flush()  # отправляем изменения в сессию

    # Сохраняем файлы, прикрепленные через file inputs
    save_files(taskFiles, "files", "task_file")
    save_files(taskImages, "images", "task_image")
    save_files(solution_files, "files", "solution_file")
    save_files(solution_images, "images", "solution_image")

    # Перемещаем временные изображения, вставленные через Quill,
    # и заменяем URL на итоговые.
    # Если требуется добавить записи attachments для этих картинок – здесь можно добавить дополнительную логику.
    task.description = move_temp_images(task.description, base_path, task_number, task.id)
    task.solution_text = move_temp_images(task.solution_text, base_path, task_number, task.id)

    db.commit()
    return task


# Эндпоинт для получения списка всех заданий
@app.get("/exam_tasks/", response_model=List[schemas.ExamTaskResponse])
async def get_exam_tasks(db: Session = Depends(get_db)):
    tasks = db.query(database.ExamTask).all()
    # Преобразуем attachments в список путей (если нужно)
    for task in tasks:
        task.attachments = [
            {"file_path": att.file_path, "file_type": att.file_type}
            for att in task.attachments
        ]
    return tasks


# Эндпоинт для отдачи файла, прикрепленного к заданию
@app.get("/exam_tasks/{task_id}/uploads/{filename}")
async def get_exam_task_file(task_id: int, filename: str):
    file_path = f"./uploads/tasks_bank/{task_id}/{task_id}/uploads/{filename}"  # измените под вашу логику
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Файл не найден")
    return FileResponse(file_path)

@app.get("/exam_tasks/{task_number}/{task_id}/uploads/{filename}")
async def get_exam_task_file(task_number: int, task_id: int, filename: str):
    file_path = f"./uploads/tasks_bank/{task_number}/{task_id}/images/{filename}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Файл не найден")
    return FileResponse(file_path)

@app.get("/exam_tasks/count_by_type", response_model=schemas.ExamTaskCountByTypeResponse)
async def count_exam_tasks_by_type(db: Session = Depends(get_db)):
    tasks = db.query(database.ExamTask).all()
    
    # Если заданий нет, возвращаем пустой объект для counts
    if not tasks:
        return {"counts": {}}
    
    counts = {}
    
    for task in tasks:
        task_type = task.task_number  # В данном случае task_number будет типом
        counts[task_type] = counts.get(task_type, 0) + 1
    
    return {"counts": counts}


@app.get("/exam_tasks/by_type/{type_id}")
def get_tasks_by_type(type_id: int, db: Session = Depends(get_db)):
    tasks = (
        db.query(database.ExamTask)
        .filter(database.ExamTask.task_number == type_id)
        .all()
    )

    result = []
    for task in tasks:
        attachments = []
        for a in task.attachments:
            cleaned_path = a.file_path.lstrip("./\\")  # сначала обрабатываем строку
            attachments.append({
                "file_path": f"{cleaned_path}",  # потом вставляем в f-string
                "attachment_type": a.attachment_type,
            })

        result.append({
            "id": task.id,
            "task_number": task.task_number,
            "description": task.description,
            "solution_text": task.solution_text,
            "correct_answer": task.correct_answer,
            "attachments": attachments,
        })

    return {"tasks": result}


@app.post("/upload_temp_image")
async def upload_temp_image(image: UploadFile = File(...)):
    temp_folder = "./uploads/temp"
    os.makedirs(temp_folder, exist_ok=True)

    # Формируем уникальное имя файла с timestamp
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    file_name = f"{timestamp}_{image.filename}"
    file_path = os.path.join(temp_folder, file_name)
    try:
        content = await image.read()
        with open(file_path, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки файла: {str(e)}")
    # Возвращаем временный URL (он будет заменён при сохранении задания)
    image_url = f"http://localhost:8000/uploads/temp/{file_name}"
    return JSONResponse(content={"image_url": image_url})

import re
import shutil
def move_temp_images(html: str, base_path: str, task_number: int, task_id: int) -> str:
    """
    Ищет ссылки на временные изображения (uploads/temp) в HTML,
    перемещает файлы в папку base_path/images и заменяет URL на итоговые.
    Итоговый URL формируется как:
      http://localhost:8000/uploads/tasks_bank/{task_number}/{task_id}/images/{filename}
    """
    pattern = r'src="(http://localhost:8000/uploads/temp/([^"]+))"'
    matches = re.findall(pattern, html)
    new_html = html
    for full_url, filename in matches:
        temp_path = os.path.join("./uploads/temp", filename)
        dest_folder = os.path.join(base_path, "images")
        os.makedirs(dest_folder, exist_ok=True)
        dest_path = os.path.join(dest_folder, filename)
        if os.path.exists(temp_path):
            shutil.move(temp_path, dest_path)
            final_url = f"http://localhost:8000/uploads/tasks_bank/{task_number}/{task_id}/images/{filename}"
            new_html = new_html.replace(full_url, final_url)
    return new_html


@app.get("/exam_tasks/{id}", response_model=schemas.ExamTaskResponse)
def get_exam_task(id: int, db: Session = Depends(get_db)):
    task = db.query(database.ExamTask).filter(database.ExamTask.id == id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задание не найдено")
    
    # Обрабатываем вложения, чтобы изменить путь (например, убрать "./" в начале)
    attachments = []
    for a in task.attachments:
        cleaned_path = a.file_path.lstrip("./\\")
        attachments.append({
            "id": a.id,
            "exam_task_id": a.exam_task_id,
            "file_path": cleaned_path,
            "attachment_type": a.attachment_type,
            "uploaded_at": a.uploaded_at,
        })

    # Собираем словарь с данными задания
    task_data = {
        "id": task.id,
        "task_number": task.task_number,
        "description": task.description,
        "answer_format": task.answer_format,
        "correct_answer": task.correct_answer,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
        "attachments": attachments,
    }
    return task_data



from fastapi.responses import StreamingResponse
import asyncio
@app.get("/sse/timer")
async def sse_timer(session_id: int, db: Session = Depends(get_db)):
    session = db.query(database.TestSession).filter(database.TestSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Сессия не найдена")
    
    end_time = session.expires_at

    async def event_generator():
        while True:
            now = datetime.utcnow()
            remaining = (end_time - now).total_seconds()
            if remaining <= 0:
                yield "data: Test finished\n\n"
                break
            yield f"data: {int(remaining)}\n\n"
            await asyncio.sleep(1)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.post("/testing/start", response_model=dict)
def start_test_session(test_type: str = Form(...), user_id: int = Form(...), db: Session = Depends(get_db)):
    # Проверяем, есть ли активная сессия для данного пользователя, которая не завершена и не истекла
    active_session = db.query(database.TestSession)\
        .filter(database.TestSession.user_id == user_id, database.TestSession.is_completed == 0, database.TestSession.expires_at > datetime.utcnow())\
        .first()
    if active_session:
        # Если сессия уже существует, возвращаем её данные
        return {
            "session_id": active_session.id,
            "task_ids": json.loads(active_session.task_ids),
            "expires_at": active_session.expires_at.isoformat()
        }

    # Если активной сессии нет, создаём новую:
    selected_tasks = []
    for task_number in range(1, 28):
        tasks = db.query(database.ExamTask).filter(database.ExamTask.task_number == task_number).all()
        if tasks:
            selected = random.choice(tasks)
            selected_tasks.append(selected.id)
        else:
            selected_tasks.append(0)
    
    if test_type == "train":
        expires_at = datetime.utcnow() + timedelta(minutes=30)
    else:
        expires_at = datetime.utcnow() + timedelta(minutes=120)
    
    task_ids_json = json.dumps(selected_tasks)
    session = database.TestSession(
        user_id=user_id,
        task_ids=task_ids_json,
        expires_at=expires_at,
        answers="{}"
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return {
        "session_id": session.id,
        "task_ids": selected_tasks,
        "expires_at": expires_at.isoformat()
    }


@app.post("/testing/submit_answer", response_model=dict)
def submit_test_answer(
    session_id: int = Form(...),
    task_id: int = Form(...),
    answer: str = Form(...),
    db: Session = Depends(get_db)
):
    session = db.query(database.TestSession).filter(database.TestSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Сессия не найдена")
    
    answers = json.loads(session.answers or "{}")
    answers[str(task_id)] = answer
    session.answers = json.dumps(answers)
    db.commit()
    return {"message": "Ответ сохранён"}

@app.get("/testing/session/{session_id}", response_model=dict)
def get_test_session(session_id: int, db: Session = Depends(get_db)):
    session = db.query(database.TestSession).filter(database.TestSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Сессия не найдена")
    return {
        "session_id": session.id,
        "task_ids": json.loads(session.task_ids),
        "answers": json.loads(session.answers or "{}"),
        "expires_at": session.expires_at.isoformat(),
        "is_completed": bool(session.is_completed)
    }



@app.post("/testing/complete", response_model=dict)
def complete_test(session_id: int = Form(...), db: Session = Depends(get_db)):
    session = db.query(database.TestSession).filter(database.TestSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Сессия не найдена")
    session.is_completed = 1
    db.commit()
    return {"message": "Тест завершён"}


@app.get("/exam_tasks")
def list_tasks(db: Session = Depends(get_db)):
    return db.query(database.ExamTask).all()