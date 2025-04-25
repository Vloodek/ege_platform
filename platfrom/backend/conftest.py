# conftest.py (рядом с main.py, а не внутри app/)
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.database as database
from app.database import Base
from main import app, get_db

# Тестовая база на файл sqlite
TEST_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    # 1) создаём новый SQLite-движок
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )

    # 2) подменяем production-движок и SessionLocal
    database.engine = engine
    database.SessionLocal = TestingSessionLocal

    # 3) сброс и создание всех таблиц
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # 4) переопределяем FastAPI-зависимость get_db
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    app.dependency_overrides[get_db] = override_get_db

    yield
    # (не удаляем test.db, он останется для отладки, или можно os.remove)

import pytest_asyncio
from httpx import AsyncClient, ASGITransport

@pytest_asyncio.fixture
async def client():
    """
    Асинхронный HTTP-клиент для FastAPI,
    уже после подмены get_db и engine.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
