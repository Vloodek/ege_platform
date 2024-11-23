from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

DATABASE_URL = "sqlite:///./test.db"  # Убедитесь, что путь к базе данных указан правильно

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String, default="student")  # Поле для роли пользователя (student/teacher)

def init_db():
    """Создание таблиц в базе данных"""
    Base.metadata.create_all(bind=engine)
