# main.py

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
from typing import List
from fastapi.responses import FileResponse
import json
from app.database import init_db  # Импортируем функцию инициализации БД
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
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
        "role": db_user.role,
        "id": db_user.id,  # Возвращаем id пользователя
        "group_id": db_user.group_id  # Добавляем номер группы
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
        group_id=group_id,  # Сохраняем ID группы
    )
    db.add(db_lesson)
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
        group_id=lesson.group_id  
    )
    db.add(db_homework)
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

    if request.url.path.startswith("/uploads/") or request.url.path == "/favicon.ico":  # Исключение для маршрутов /uploads/
        return await call_next(request)

    excluded_routes = ["/register", "/login"]  # Маршруты, где не требуется токен
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
    client_submission_time: Optional[str] = Form(None),
    files: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_db)
):
    # Определяем клиентское время: если пришло, пытаемся распарсить, иначе берем текущее время
    if client_submission_time:
        try:
            client_time = datetime.fromisoformat(client_submission_time)
        except Exception as e:
            client_time = datetime.utcnow()
    else:
        client_time = datetime.utcnow()

    # Создаем запись отклика с клиентским временем
    submission = database.HomeworkSubmission(
        homework_id=homework_id,
        user_id=user_id,
        comment=comment,
        submission_date=datetime.utcnow(),  # серверное время
        client_submission_time=client_time
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)

    # Получаем домашнее задание, чтобы определить lesson_id
    homework_obj = db.query(database.Homework).filter(database.Homework.id == homework_id).first()
    if not homework_obj:
        raise HTTPException(status_code=404, detail="Домашнее задание не найдено")
    lesson_id = homework_obj.lesson_id

    # Формируем базовый путь для откликов: uploads/<lesson_id>/homework/
    base_homework_folder = os.path.join(UPLOAD_FOLDER, str(lesson_id), "homework")
    os.makedirs(base_homework_folder, exist_ok=True)

    # Создаем папку для отклика по user_id (без даты)
    submission_folder = os.path.join(base_homework_folder, str(user_id))
    os.makedirs(submission_folder, exist_ok=True)

    # Сохраняем файлы отклика в созданную папку
    if files:
        for file in files:
            file_location = os.path.join(submission_folder, file.filename)
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
    submission_files = db.query(database.HomeworkFile)\
                         .filter(database.HomeworkFile.submission_id == submission.id)\
                         .all()
    file_paths = [file.file_path for file in submission_files]
    return {
        "id": submission.id,
        "homework_id": submission.homework_id,
        "user_id": submission.user_id,
        "submission_date": submission.submission_date.isoformat(),
        "grade": submission.grade,
        "status": submission.status,
        "comment": submission.comment,
        "client_submission_time": submission.client_submission_time.isoformat() if submission.client_submission_time else None,
        "files": file_paths
    }


@app.put("/update_submission/{submission_id}")
async def update_submission(
    submission_id: int,
    comment: str = Form(...),
    client_submission_time: Optional[str] = Form(None),
    files: Optional[List[UploadFile]] = File(None),
    files_to_delete: str = Form("[]"),  # JSON-список файлов для удаления
    db: Session = Depends(get_db)
):
    submission = db.query(database.HomeworkSubmission).filter(database.HomeworkSubmission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Ответ не найден")

    # Обновляем комментарий и время отправки
    submission.comment = comment
    submission.submission_date = datetime.utcnow()
    try:
        submission.client_submission_time = datetime.fromisoformat(client_submission_time) if client_submission_time else datetime.utcnow()
    except Exception:
        submission.client_submission_time = datetime.utcnow()

    # Удаление файлов
    files_to_delete = json.loads(files_to_delete)  # Преобразуем JSON-строку в список

    if files_to_delete:
        for file_path in files_to_delete:
            # Преобразуем путь в формат с обратными слэшами, как в базе данных
            full_path = file_path.replace("/", "\\")  # Заменяем прямые слэши на обратные

            # Выводим путь для отладки
            print(f"Пытаемся удалить файл: {full_path}")

            # Удаляем физический файл
            if os.path.exists(full_path):
                os.remove(full_path)
                print(f"Файл удалён: {full_path}")
            else:
                print(f"Файл не найден на диске: {full_path}")

            # Логирование, если запись о файле есть в БД
            file_record = db.query(database.HomeworkFile).filter(database.HomeworkFile.file_path == full_path).first()
            if file_record:
                db.query(database.HomeworkFile).filter(database.HomeworkFile.file_path == full_path).delete()
                print(f"Запись о файле с путём {full_path} удалена из БД")
            else:
                print(f"Запись о файле с путём {full_path} не найдена в БД")

    # Если передаются новые файлы, сохраняем их
    if files:
        homework_obj = db.query(database.Homework).filter(database.Homework.id == submission.homework_id).first()
        lesson_id = homework_obj.lesson_id if homework_obj else "default"
        submission_folder = os.path.join("uploads", str(lesson_id), "homework", str(submission.user_id))
        os.makedirs(submission_folder, exist_ok=True)

        for file in files:
            file_location = os.path.join(submission_folder, file.filename)
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
    submission = db.query(database.HomeworkSubmission).filter(database.HomeworkSubmission.id == submission_id).first()

    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    submission.grade = grade
    submission.status = "graded"

    db_grade = database.Grade(submission_id=submission.id, grade=grade)
    db.add(db_grade)
    db.commit()
    
    return {"message": "Grade assigned successfully"}

import random
import string

def generate_group_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

@app.post("/groups/", response_model=schemas.GroupResponse)
async def create_group(group: schemas.GroupCreate, db: Session = Depends(get_db)):
    group_code = generate_group_code()
    db_group = database.Group(name=group.name, code=group_code)
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
    print(f"📥 Получен запрос с кодом группы: {group_code}")
    print(f"🔹 Заголовки запроса: {request.headers}")
    print(f"🔹 Данные из тела запроса: {body}")

    # Ищем группу по коду
    group = db.query(database.Group).filter(database.Group.code == group_code).first()
    if not group:
        return JSONResponse(status_code=404, content={"message": "Группа не найдена"})

    # Ищем пользователя
    user = db.query(database.User).filter(database.User.id == body.user_id).first()
    if not user:
        return JSONResponse(status_code=404, content={"message": "Пользователь не найден"})

    # Обновляем group_id у пользователя
    user.group_id = group.id
    db.commit()

    return {"message": f"Пользователь {user.name} успешно добавлен в группу {group.name}"}

#список всех групп
@app.get("/groups/", response_model=List[schemas.GroupResponse])
async def get_groups(db: Session = Depends(get_db)):
    groups = db.query(database.Group).all()
    return groups



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

import shutil
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

# Роутер для работы с откликами на домашки
@app.get("/api/homework/{homework_id}/submissions")
async def get_submissions(homework_id: int, db: Session = Depends(get_db)):
    # Получаем домашку по ID
    homework = db.query(database.Homework).filter(database.Homework.id == homework_id).first()
    if not homework:
        raise HTTPException(status_code=404, detail="Homework not found")

    # Получаем все отклики на данную домашку
    submissions = db.query(database.HomeworkSubmission).filter(database.HomeworkSubmission.homework_id == homework_id).all()
    
    result = []
    for submission in submissions:
        user = db.query(database.User).filter(database.User.id == submission.user_id).first()
        if user:
            result.append({
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "status": submission.status,  # Можно адаптировать кода для отображения статуса
            })
    
    return result