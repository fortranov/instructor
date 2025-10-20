"""
Тест создания свежей базы данных (имитация продакшена)
"""

import os
import sqlite3
from database import create_tables, ensure_database_compatibility, Base, engine

def test_fresh_database():
    """Тестируем создание базы данных с нуля"""
    
    # Создаем временную базу данных
    test_db_path = "./test_fresh.db"
    
    # Удаляем файл базы данных, если он существует
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
        print(f"Удален существующий файл: {test_db_path}")
    
    # Временно меняем путь к базе данных
    original_db_path = os.environ.get("DB_PATH", "./triplan.db")
    os.environ["DB_PATH"] = test_db_path
    
    try:
        print("🔄 Создаем свежую базу данных...")
        
        # Пересоздаем движок с новым путем
        from database import SQLALCHEMY_DATABASE_URL
        from sqlalchemy import create_engine
        test_engine = create_engine(f"sqlite:///{test_db_path}", connect_args={"check_same_thread": False})
        
        # Очищаем метаданные и создаем таблицы
        Base.metadata.clear()
        Base.metadata.create_all(bind=test_engine)
        
        print("✅ Таблицы созданы")
        
        # Проверяем структуру таблицы users
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(users);")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print(f"📋 Колонки в таблице users: {column_names}")
        
        # Проверяем наличие всех необходимых колонок
        required_columns = [
            'id', 'uin', 'email', 'hashed_password', 'first_name', 'last_name',
            'is_active', 'preferred_workout_days', 'competition_date', 
            'competition_type', 'tariff_id', 'created_at', 'updated_at'
        ]
        
        missing_columns = []
        for col in required_columns:
            if col not in column_names:
                missing_columns.append(col)
        
        if missing_columns:
            print(f"❌ Отсутствующие колонки: {missing_columns}")
        else:
            print("✅ Все необходимые колонки присутствуют в таблице users")
        
        # Проверяем наличие таблицы tariffs
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tariffs';")
        if cursor.fetchone():
            print("✅ Таблица tariffs создана")
            
            cursor.execute("PRAGMA table_info(tariffs);")
            tariff_columns = cursor.fetchall()
            tariff_column_names = [col[1] for col in tariff_columns]
            print(f"📋 Колонки в таблице tariffs: {tariff_column_names}")
        else:
            print("❌ Таблица tariffs не создана")
        
        # Проверяем наличие таблицы workout_coefficients
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='workout_coefficients';")
        if cursor.fetchone():
            print("✅ Таблица workout_coefficients создана")
            
            cursor.execute("PRAGMA table_info(workout_coefficients);")
            coeff_columns = cursor.fetchall()
            coeff_column_names = [col[1] for col in coeff_columns]
            print(f"📋 Колонки в таблице workout_coefficients: {coeff_column_names}")
        else:
            print("❌ Таблица workout_coefficients не создана")
        
        # Проверяем все таблицы
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]
        print(f"📋 Все созданные таблицы: {table_names}")
        
        conn.close()
        
        print("\n🎯 Результат теста:")
        if not missing_columns:
            print("✅ База данных создается корректно со всеми необходимыми колонками")
            print("✅ Готова для продакшена!")
        else:
            print("❌ Есть проблемы с созданием базы данных")
        
    except Exception as e:
        print(f"❌ Ошибка при создании базы данных: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Восстанавливаем оригинальный путь
        os.environ["DB_PATH"] = original_db_path
        
        # Удаляем тестовую базу данных
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
            print(f"🗑️ Удален тестовый файл: {test_db_path}")

if __name__ == "__main__":
    test_fresh_database()
