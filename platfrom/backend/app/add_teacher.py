from database import SessionLocal, User
from passlib.context import CryptContext

# Инициализация контекста для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def add_teacher(name: str, email: str, password: str):
    db = SessionLocal()
    try:
        # Проверка, существует ли уже преподаватель
        existing_teacher = db.query(User).filter(User.role == "teacher").first()
        if existing_teacher:
            print("Преподаватель уже существует: ", existing_teacher.email)
            return
        
        # Проверка, существует ли пользователь с таким email
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print("Пользователь с таким email уже существует.")
            return

        # Добавление нового преподавателя
        teacher = User(
            name=name,
            email=email,
            password=hash_password(password),  # Хешируем пароль
            role="teacher"
        )
        db.add(teacher)
        db.commit()
        db.refresh(teacher)
        print(f"Преподаватель {teacher.name} добавлен с email {teacher.email}.")
    finally:
        db.close()

# Вызов функции для добавления преподавателя
if __name__ == "__main__":
    name = input("Введите имя преподавателя: ")
    email = input("Введите email преподавателя: ")
    password = input("Введите пароль преподавателя: ")
    add_teacher(name, email, password)
