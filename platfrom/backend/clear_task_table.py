from sqlalchemy.orm import Session
import app.database as database  # Импортируем базу данных
from app.models import Task  # Импортируем модель Task

# Инициализация базы данных
database.init_db()  # Инициализация базы данных (если база данных не существует, она будет создана)

# Функция для очистки таблицы Task
def clear_tasks():
    # Получаем сессию базы данных
    db: Session = database.SessionLocal()
    try:
        # Удаляем все записи из таблицы Task
        db.query(Task).delete()
        db.commit()
        print("Все задачи были успешно удалены.")
    except Exception as e:
        db.rollback()
        print("Произошла ошибка при удалении задач:", e)
    finally:
        db.close()

# Запускаем функцию
if __name__ == "__main__":
    clear_tasks()
