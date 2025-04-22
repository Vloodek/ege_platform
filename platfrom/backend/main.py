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

@app.post("/lessons/", response_model=schemas.LessonResponse)
async def create_lesson(
    name: str = Form(...),
    description: str = Form(...),
    text: str = Form(...),
    date: datetime = Form(...),
    group_id: int = Form(...),
    images: list[UploadFile] = File(default=[]),
    files:  list[UploadFile] = File(default=[]),
    db: Session = Depends(get_db),
):
    # 1) Создаём урок
    lesson = database.Lesson(name=name, description="", text="", date=date)
    db.add(lesson); db.commit(); db.refresh(lesson)

    # 2) Привязываем к группе
    grp = db.query(database.StudyGroup).get(group_id)
    if grp:
        lesson.groups.append(grp)
        db.commit()

    # 3) Подготовка папок
    base = os.path.join(UPLOAD_FOLDER, str(lesson.id))
    os.makedirs(os.path.join(base, "files"),  exist_ok=True)
    os.makedirs(os.path.join(base, "images"), exist_ok=True)

    # 4) Сохраняем простые файлы/картинки
    file_paths = []
    for f in files:
        p = os.path.join(base, "files", f.filename)
        with open(p, "wb") as buf: buf.write(f.file.read())
        file_paths.append(p.replace("\\","/"))

    image_paths = []
    for img in images:
        p = os.path.join(base, "images", img.filename)
        with open(p, "wb") as buf: buf.write(img.file.read())
        image_paths.append(p.replace("\\","/"))

    # 5) Переносим Quill‑temp‑изображения из HTML
    new_desc, moved_desc = move_temp_images(
        description, base, lesson.id, "lesson_image", db
    )
    new_text, moved_text = move_temp_images(
        text,        base, lesson.id, "lesson_image", db
    )
    lesson.description = new_desc
    lesson.text        = new_text

    # 6) Записываем пути в БД как строку (VARCHAR)
    all_files  = file_paths
    all_images = image_paths + [
        os.path.join(base, "images", fn).replace("\\","/")
        for fn in moved_desc + moved_text
    ]
    lesson.files       = ",".join(all_files)
    lesson.image_links = ",".join(all_images)

    db.commit(); db.refresh(lesson)

    # 7) Для ответа FastAPI конвертируем обратно в список
    lesson.files       = lesson.files.split(",")       if lesson.files else []
    lesson.image_links = lesson.image_links.split(",") if lesson.image_links else []
    return lesson

@app.delete("/lessons/{lesson_id}", status_code=204)
async def delete_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
):
    # 1) Получаем урок
    lesson = db.query(database.Lesson).get(lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    # 2) Удаляем все домашки, связанные с уроком
    #    (предполагается, что в модели Lesson есть relationship .homeworks)
    for hw in list(lesson.homeworks):
        # 2.1) Разрываем связи many-to-many у домашки
        hw.groups.clear()
        db.commit()
        # 2.2) Удаляем саму домашку из БД
        db.delete(hw)
    db.commit()

    # 3) Удаляем папку урока вместе с файлами и домашками
    lesson_folder = os.path.join(UPLOAD_FOLDER, str(lesson.id))
    if os.path.exists(lesson_folder):
        shutil.rmtree(lesson_folder)

    # 4) Очищаем связи урока с группами
    lesson.groups.clear()
    db.commit()

    # 5) Удаляем сам урок
    db.delete(lesson)
    db.commit()

    return  # 204 No Content



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
    lesson = db.query(database.Lesson).get(lesson_id)
    if not lesson:
        raise HTTPException(404, "Урок не найден")

    # 1) Создаем домашку
    hw = database.Homework(lesson_id=lesson_id, description="", text="", date=date)
    db.add(hw)
    db.commit()
    db.refresh(hw)

    # 2) Привязываем к тем же группам
    for grp in lesson.groups:
        hw.groups.append(grp)
    db.commit()

    # 3) Папки
    base = os.path.join(UPLOAD_FOLDER, str(lesson_id), "homework")
    os.makedirs(os.path.join(base, "files"), exist_ok=True)
    os.makedirs(os.path.join(base, "images"), exist_ok=True)

    # 4) Сохраняем обычные файлы и картинки
    file_paths = []
    if files:
        for f in files:
            p = os.path.join(base, "files", f.filename)
            with open(p, "wb") as buf: buf.write(f.file.read())
            file_paths.append(p.replace("\\","/"))

    image_paths = []
    if images:
        for img in images:
            p = os.path.join(base, "images", img.filename)
            with open(p, "wb") as buf: buf.write(img.file.read())
            image_paths.append(p.replace("\\","/"))

    # 5) Переносим temp‑изображения
    new_desc, moved_desc = move_temp_images(
        description, base, lesson_id, "homework_image", db
    )
    new_text, moved_text = move_temp_images(
        text,        base, lesson_id, "homework_image", db
    )
    hw.description = new_desc
    hw.text        = new_text

    # 6) Сохраняем пути
    all_files  = file_paths
    all_images = image_paths + [
        os.path.join(base, "images", fn).replace("\\","/")
        for fn in moved_desc + moved_text
    ]
    hw.files  = json.dumps(all_files)
    hw.images = json.dumps(all_images)

    db.commit()
    db.refresh(hw)

    # 7) Для ответа распарсим обратно
    hw.files  = json.loads(hw.files)  if hw.files  else []
    hw.images = json.loads(hw.images) if hw.images else []

    return hw





@app.get("/homeworks/", response_model=List[schemas.HomeworkResponse])
async def get_homeworks(db: Session = Depends(get_db)):
    homeworks = db.query(database.Homework).all()
    for homework in homeworks:
        homework.files = json.loads(homework.files) if homework.files else []
        # Убираем обработку images, если она не нужна
        homework.images = []  # Можно просто очистить список или убрать строку
    return homeworks

@app.get("/homeworks/with-status")
def get_homeworks_with_status(
    db: Session = Depends(get_db),
    request: Request = None
):
    user_email = getattr(request.state, "user", None)
    if not user_email:
        raise HTTPException(status_code=401, detail="Не авторизован")

    user = db.query(database.User).filter(database.User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    homeworks = db.query(database.Homework).all()
    result = []

    for hw in homeworks:
        submission = db.query(database.HomeworkSubmission).filter_by(
            homework_id=hw.id,
            user_id=user.id
        ).order_by(database.HomeworkSubmission.id.desc()).first()

        if submission is None:
            status = "not_submitted"
        elif submission.status == "graded":
            status = "graded"
        elif submission.status == "response_received":
            status = "response_received"
        elif submission.status in ["submitted", "waiting"]:
            status = "submitted"
        else:
            status = "not_submitted"

        result.append({
            "id": hw.id,
            "lesson_id": hw.lesson_id,
            "description": hw.description,
            "date": hw.date.isoformat(),
            "status": status
        })

    return result

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

@app.delete("/groups/{group_id}", status_code=204)
async def delete_group(group_id: int, db: Session = Depends(get_db)):
    group = db.query(database.StudyGroup).filter(database.StudyGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    db.delete(group)
    db.commit()
    return  # статус 204 - пустой ответ

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
            file_location = os.path.join(homework_folder, "files", file.filename)
            os.makedirs(os.path.dirname(file_location), exist_ok=True)
            with open(file_location, "wb") as f:
                f.write(file.file.read())
            file_paths.append(file_location)

    if images:
        for image in images:
            image_location = os.path.join(homework_folder, "images", image.filename)
            os.makedirs(os.path.dirname(image_location), exist_ok=True)
            with open(image_location, "wb") as f:
                f.write(image.file.read())
            image_paths.append(image_location)

    # Переносим temp‑изображения
    new_desc, moved_desc = move_temp_images(
        description, homework_folder, lesson_id, "homework_image", db
    )
    new_text, moved_text = move_temp_images(
        text, homework_folder, lesson_id, "homework_image", db
    )
    
    # Обновляем описание и текст
    db_homework.description = new_desc
    db_homework.text = new_text

    # Обновляем пути
    all_files = file_paths
    all_images = image_paths + [
        os.path.join(homework_folder, "images", fn).replace("\\", "/")
        for fn in moved_desc + moved_text
    ]
    
    db_homework.files = json.dumps(all_files)
    db_homework.images = json.dumps(all_images)

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
    task.description, _ = move_temp_images(
    html=task.description,
    base_path=base_path,
    owner_id=task.id,
    attachment_type="task_image",
    db=db
)

    task.solution_text, _ = move_temp_images(
        html=task.solution_text,
        base_path=base_path,
        owner_id=task.id,
        attachment_type="solution_image",
        db=db
    )


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
from bs4 import BeautifulSoup
# ловим как абсолютные, так и относительные ссылки на temp
# Ищет src="/uploads/temp/<filename>"
TEMP_SRC_PATTERN = re.compile(r'src="(?:https?://[^/]+)?/uploads/temp/([^"]+)"')
from typing import Tuple, List
def move_temp_images(
    html: str,
    base_path: str,
    owner_id: int,
    attachment_type: str,
    db: Session,
    url_prefix: str = "/uploads"
) -> Tuple[str, List[str]]:
    """
    1) Парсит HTML через BeautifulSoup.
    2) Ищет все <img> с src, содержащим '/uploads/temp/'.
    3) Переносит файлы из './uploads/temp' -> 'base_path/images'.
    4) Меняет в HTML src на '/uploads/.../images/...'.
    5) (Опционально) создает запись Attachment в БД.
    Возвращает (new_html, [имена файлов]).
    """
    soup = BeautifulSoup(html, "html.parser")
    moved: List[str] = []
    images_dir = os.path.join(base_path, "images")
    os.makedirs(images_dir, exist_ok=True)

    for img in soup.find_all("img"):
        src = img.get("src", "")
        if "/uploads/temp/" not in src:
            continue

        filename = src.rsplit("/uploads/temp/", 1)[1]
        temp_path = os.path.join("uploads", "temp", filename)
        if not os.path.exists(temp_path):
            continue

        # Переносим файл
        dest_path = os.path.join(images_dir, filename)
        shutil.move(temp_path, dest_path)

        # Новый web‑URL
        rel = os.path.normpath(dest_path).replace("\\", "/")
        idx = rel.find("uploads")
        new_src = "/" + rel[idx:]
        img["src"] = new_src
        moved.append(filename)

        # — если нужна Attachment-модель — раскомментируйте:
        # from app.database import LessonAttachment
        # att = LessonAttachment(
        #     owner_id=owner_id,
        #     file_path=rel,
        #     attachment_type=attachment_type,
        # )
        # db.add(att)

    return str(soup), moved


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
        "solution_text": task.solution_text,  # ⬅️ вот это
        "created_at": task.created_at,
        "updated_at": task.updated_at,
        "attachments": attachments,
    }
    print(task_data)

    # Специальная логика для задания 25
    if task.task_number == 25:
        task_data['is_task_25'] = True

    # Специальная логика для заданий 26 и 27: принудительный ввод в формате таблицы 1×2
    if task.task_number in [26, 27]:
        task_data['is_table_1x2'] = True

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

    now = datetime.utcnow()
    is_expired = session.expires_at <= now
    is_completed = bool(session.is_completed)

    if is_completed:
        status = "completed"
    elif is_expired:
        status = "expired"
    else:
        status = "active"

    return {
        "session_id": session.id,
        "task_ids": json.loads(session.task_ids),
        "answers": json.loads(session.answers or "{}"),
        "expires_at": session.expires_at.isoformat(),
        "is_completed": is_completed,
        "status": status  # 👈 добавляем статус
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




def normalize_answer(answer_str: str, column_count: int = None) -> list:
    try:
        arr = json.loads(answer_str)
        # Если ответ является одномерным массивом, оборачиваем его в список (1 строка)
        if arr and all(not isinstance(x, list) for x in arr):
            arr = [arr]
        normalized = [row for row in arr if any(cell.strip() for cell in row)]
        if column_count:
            normalized = [row + [""] * (column_count - len(row)) for row in normalized]
        return normalized
    except Exception as e:
        print("Ошибка парсинга:", e)
        return []



def get_column_count(answer_str: str) -> int:
    try:
        arr = json.loads(answer_str)
        # Если ответ является одномерным массивом, оборачиваем его в список (1 строка)
        if arr and all(not isinstance(x, list) for x in arr):
            arr = [arr]
        return max(len(row) for row in arr if isinstance(row, list))
    except Exception as e:
        print("Ошибка определения количества колонок:", e)
        return 1





@app.get("/testing/results", response_model=dict)
def get_test_results(session_id: int, db: Session = Depends(get_db)):
    session = db.query(database.TestSession).filter(database.TestSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Сессия не найдена")
    
    user_answers = json.loads(session.answers or "{}")
    task_ids = json.loads(session.task_ids)
    results = {}
    total_score = 0

    for task_id in task_ids:
        task = db.query(database.ExamTask).filter(database.ExamTask.id == task_id).first()
        if not task:
            continue

        correct_raw = task.correct_answer or ""
        user_answer_raw = user_answers.get(str(task_id), "")
        print(f"Task {task_id} - корректный ответ (raw): {correct_raw}")
        print(f"Task {task_id} - ответ пользователя (raw): {user_answer_raw}")

        if task.answer_format in ["tableDyn1Col", "tableDyn2Col", "table10"] or task.task_number in [26, 27]:
            column_count = get_column_count(correct_raw)
            correct_norm = normalize_answer(correct_raw, column_count)
            user_norm = normalize_answer(user_answer_raw, column_count)
            print(f"Task {task_id} - нормализованный корректный ответ: {correct_norm}")
            print(f"Task {task_id} - нормализованный ответ пользователя: {user_norm}")
            is_correct = user_norm == correct_norm
        else:
            is_correct = user_answer_raw.strip().lower() == correct_raw.strip().lower()


        results[task_id] = is_correct
        if is_correct:
            total_score += 2 if task.task_number in [26, 27] else 1

    print("Итоговые результаты:", results, "итоговый счет:", total_score)
    return {
        "results": results,
        "score": total_score
    }




@app.get("/testing/solutions", response_model=dict)
def get_test_solutions(session_id: int, db: Session = Depends(get_db)):
    # Получаем сессию тестирования
    session = db.query(database.TestSession).filter(database.TestSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Сессия не найдена")
    
    # Извлекаем список идентификаторов заданий
    task_ids = json.loads(session.task_ids)
    solutions = {}
    
    # Для каждого задания получаем текст решения
    for task_id in task_ids:
        task = db.query(database.ExamTask).filter(database.ExamTask.id == task_id).first()
        if task:
            # Если поле solution_text отсутствует или пустое, возвращаем сообщение о его отсутствии
            solutions[task_id] = task.solution_text or "Решение отсутствует"
    
    return {"solutions": solutions}


import stat
def force_rmtree(path):
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            file_path = os.path.join(root, name)
            try:
                os.chmod(file_path, stat.S_IWRITE)
                os.remove(file_path)
            except Exception as e:
                os.remove(file_path)
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(path)

@app.delete("/exam_tasks/{id}", response_model=dict)
def delete_exam_task(id: int, db: Session = Depends(get_db)):
    task = db.query(database.ExamTask).filter(database.ExamTask.id == id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задание не найдено")
    
    # Формируем путь к папке с данными задания
    base_path = f"./uploads/tasks_bank/{task.task_number}/{task.id}"
    if os.path.exists(base_path):
        try:
            force_rmtree(base_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ошибка удаления файлов: {str(e)}")
    
    # Если attachments связаны через каскадное удаление, то удаление задания удалит их,
    # иначе вручную можно удалить записи attachments (здесь мы просто удаляем само задание)
    db.delete(task)
    db.commit()
    return {"message": "Задание удалено"}



@app.get("/schedule")
def get_schedule(
    month: int,
    year: int,
    type: str = Query("lessons", enum=["lessons", "homeworks"]),
    db: Session = Depends(get_db),
    request: Request = None
):
    try:
        start_date = datetime(year, month, 1)
        end_date = datetime(year + 1, 1, 1) if month == 12 else datetime(year, month + 1, 1)
    except ValueError:
        raise HTTPException(status_code=400, detail="Неверная дата")

    # Получаем пользователя из токена
    user_email = getattr(request.state, "user", None)
    if not user_email:
        raise HTTPException(status_code=401, detail="Не авторизован")

    user = db.query(database.User).filter(database.User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    current_user_id = user.id

    if type == "lessons":
        lessons = db.query(database.Lesson).filter(
            database.Lesson.date >= start_date,
            database.Lesson.date < end_date
        ).all()
        return [
            {
                "id": lesson.id,
                "name": lesson.name,
                "date": lesson.date.isoformat()
            }
            for lesson in lessons
        ]

    elif type == "homeworks":
        homeworks = db.query(database.Homework).filter(
            database.Homework.date >= start_date,
            database.Homework.date < end_date
        ).all()
        result = []

        for hw in homeworks:
            submission = db.query(database.HomeworkSubmission).filter_by(
                homework_id=hw.id, user_id=current_user_id
            ).order_by(database.HomeworkSubmission.id.desc()).first()

            if submission is None:
                dot = "red"
                raw_status = "not submitted"
            elif submission.status == "graded":
                dot = "green"
                raw_status = submission.status
            elif submission.status == "response_received":
                dot = "orange"
                raw_status = submission.status
            elif submission.status in ["submitted", "waiting"]:
                dot = "gray"
                raw_status = submission.status
            else:
                dot = "red"
                raw_status = submission.status


            hw_name = hw.description.strip() if hw.description and hw.description.strip() else "Домашнее задание"

            result.append({
                "id": hw.lesson_id,
                "name": hw_name,
                "date": hw.date.isoformat(),
                "submission_status": dot,
                "raw_status": raw_status
            })

        return result
    


@app.post("/homework_tests/", response_model=schemas.HomeworkTestResponse)
async def create_homework_test(
    lesson_id: int = Form(...),
    duration: int = Form(...),
    tasks_meta: str = Form(...),  # JSON string of list[dict]
    task_files: List[UploadFile] = File(default=[]),
    db: Session = Depends(get_db),
):
    # 1. Создаём запись теста
    test = database.HomeworkTest(lesson_id=lesson_id, duration=duration, tasks_meta=tasks_meta)
    db.add(test); db.commit(); db.refresh(test)

    base = os.path.join(UPLOAD_FOLDER, str(lesson_id), "test", str(test.id))
    os.makedirs(os.path.join(base, "files"), exist_ok=True)
    os.makedirs(os.path.join(base, "images"), exist_ok=True)

    # 2. Сохраняем все файлы и строим карту filename → путь
    file_map: dict[str,str] = {}
    for file in task_files:
        file.file.seek(0)
        filepath = os.path.join(base, "files", file.filename)
        with open(filepath, "wb") as f:
            f.write(file.file.read())
        db.add(database.HomeworkTestAttachment(
            test_id=test.id,
            file_path=filepath.replace("\\", "/"),
            attachment_type="test_file"
        ))
        file_map[file.filename] = filepath.replace("\\", "/")
    db.commit()

    # 3. Парсим мету задач и для каждой задачи берём только её файлы по имени
    try:
        tasks = json.loads(tasks_meta)
        for task in tasks:
            # если в JSON‑мете лежат оригинальные имена файлов
            originals = task.get("files", [])
            # отфильтруем по нашей карте
            task["files"] = [file_map[name] for name in originals if name in file_map]

            # обработка картинок в описании как раньше
            if "description" in task:
                new_desc, moved_imgs = move_temp_images(
                    task["description"], base, test.lesson_id, "test_image", db
                )
                task["description"] = new_desc
                task["images"] = moved_imgs
        # сохраняем обновлённую мету
        test.tasks_meta = json.dumps(tasks)
        db.commit()
    except Exception as e:
        raise HTTPException(400, f"Невалидный формат tasks_meta: {e}")

    return test



@app.get(
    "/homework_tests/{test_id}",
    response_model=schemas.HomeworkTestFullResponse,
)
def read_homework_test(test_id: int, db: Session = Depends(get_db)):
    test = db.query(database.HomeworkTest).filter_by(id=test_id).first()
    if not test:
        raise HTTPException(404, detail="HomeworkTest not found")

    try:
        raw_tasks = json.loads(test.tasks_meta)
    except json.JSONDecodeError:
        raise HTTPException(500, detail="Invalid tasks_meta JSON")

    # Собираем задачи прямо из tasks_meta
    result_tasks = []
    for idx, t in enumerate(raw_tasks):
        result_tasks.append({
            "id":              idx,                      # или t.get("id", idx)
            "title":           t.get("title", ""),
            "description":     t.get("description", ""),
            "correct_answer":  t.get("correct_answer", ""),
            "files":           t.get("files", []),
            "images":          t.get("images", []),       # у тебя в мета этого поля нет — будет []
        })

    return {
        "id":          test.id,
        "homework_id": test.lesson_id,
        "duration":    test.duration,
        "tasks":       result_tasks,
    }

@app.get(
    "/homework_tests/by_lesson/{lesson_id}",
    response_model=schemas.HomeworkTestResponse
)
def get_test_by_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
):
    # Ищем тесты по lesson_id (не через homework_id)
    test = db.query(database.HomeworkTest).filter_by(lesson_id=lesson_id).first()
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test for this lesson not found"
        )
    
    return test



@app.post("/homework_tests/{test_id}/start", response_model=dict)
def start_homework_test(
    test_id: int,
    user_id: int = Form(...),
    db: Session = Depends(get_db)
):
    # Проверяем, что тест существует
    test = db.query(database.HomeworkTest).filter_by(id=test_id).first()
    if not test:
        raise HTTPException(404, detail="HomeworkTest not found")

    # Смотрим, есть ли уже незавершённая попытка
    active = (
        db.query(database.TestSession)
          .filter_by(user_id=user_id, is_completed=0)
          .first()
    )
    if active:
        remaining = max(int((active.expires_at - datetime.utcnow()).total_seconds()), 0)
        return {"attempt_id": active.id, "remaining_time": remaining}

    # Декодируем мета‑данные, чтобы знать число задач
    try:
        tasks_meta = json.loads(test.tasks_meta)
    except json.JSONDecodeError:
        raise HTTPException(500, detail="Invalid tasks_meta JSON")

    # Вычисляем время жизни сессии
    expires = datetime.utcnow() + timedelta(minutes=test.duration)

    # *** СТАРЫЙ ФРАГМЕНТ БЫЛ БЕЗ homework_test_id ***
    new_session = database.TestSession(
        user_id=user_id,
        homework_test_id=test_id,               # ← обязательно!
        task_ids=json.dumps(list(range(len(tasks_meta)))),
        answers=json.dumps({}),
        expires_at=expires,                     # ← лучше выставить нормальное время
        is_completed=0,
        created_at=datetime.utcnow(),
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    remaining_time = max(int((expires - datetime.utcnow()).total_seconds()), 0)
    return {
        "attempt_id": new_session.id,
        "remaining_time": remaining_time,
    }


@app.get(
    "/homework_tests/session/{attempt_id}",
    response_model=schemas.HomeworkTestSessionResponse,
)
def get_homework_test_session(
    attempt_id: int,
    db: Session = Depends(get_db),
):
    sess = db.query(database.TestSession).filter_by(id=attempt_id).first()
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")

    # подтягиваем тест, к которому относится сессия
    test = db.query(database.HomeworkTest).filter_by(id=sess.homework_test_id).first()
    if not test:
        raise HTTPException(status_code=500, detail="HomeworkTest for this session not found")

    # десериализуем мету
    try:
        raw = json.loads(test.tasks_meta)
    except Exception:
        raise HTTPException(status_code=500, detail="Invalid tasks_meta JSON")

    # собираем список задач
    tasks = []
    for idx, t in enumerate(raw):
        tasks.append({
            "id":             idx,
            "title":          t.get("title", ""),
            "description":    t.get("description", ""),
            "correct_answer": t.get("correct_answer", ""),
            "files":          t.get("files", []),
            "images":         t.get("images", []),
        })

    # время до истечения
    delta = sess.expires_at - datetime.utcnow()
    remaining = max(int(delta.total_seconds()), 0)

    return {
        "attempt_id":     sess.id,
        "duration":       test.duration,
        "remaining_time": remaining,
        "tasks":          tasks,
        "answers":        json.loads(sess.answers or "{}"),
        "is_completed":   bool(sess.is_completed),
    }



@app.get("/homework_tests/session/{session_id}/results", response_model=dict)
def get_homework_test_results(session_id: int, db: Session = Depends(get_db)):
    # Получаем сессию
    session = db.query(database.TestSession).filter(database.TestSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Сессия не найдена")

    # Загружаем ответы пользователя
    user_answers = json.loads(session.answers or "{}")
    task_ids = json.loads(session.task_ids)  # Индексы задач
    results = {}
    correct_answers = {}
    total_score = 0

    # Загружаем информацию о тесте
    homework_test = db.query(database.HomeworkTest).filter(database.HomeworkTest.id == session.homework_test_id).first()
    tasks_meta = json.loads(homework_test.tasks_meta)  # Метаданные задач теста

    for task_id in task_ids:
        # Получаем задачу по индексу
        task_data = tasks_meta[task_id]  # task_id здесь — это индекс
        correct_raw = task_data["correct_answer"] or ""
        user_answer_raw = user_answers.get(str(task_id), "")  # Получаем ответ пользователя по индексу

        # Проверка на правильность ответа
        if task_data.get("answer_format") in ["tableDyn1Col", "tableDyn2Col", "table10"] or task_data.get("task_number") in [26, 27]:
            column_count = get_column_count(correct_raw)
            correct_norm = normalize_answer(correct_raw, column_count)
            user_norm = normalize_answer(user_answer_raw, column_count)
            is_correct = user_norm == correct_norm
        else:
            is_correct = user_answer_raw.strip().lower() == correct_raw.strip().lower()

        # Сохраняем результат
        results[str(task_id)] = is_correct
        correct_answers[str(task_id)] = correct_raw
        if is_correct:
            total_score += 2 if task_data.get("task_number") in [26, 27] else 1

    return {
        "results": results,
        "score": total_score,
        "correct_answers": correct_answers
    }
