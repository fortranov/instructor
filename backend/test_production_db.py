"""
Тест создания базы данных для продакшена
"""

import os
import sqlite3
import tempfile

def test_production_database():
    """Тестируем создание базы данных как в продакшене"""
    
    # Создаем временный файл для базы данных
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        test_db_path = tmp_file.name
    
    print(f"🔄 Создаем тестовую базу данных: {test_db_path}")
    
    try:
        # Импортируем модули после создания временного файла
        from sqlalchemy import create_engine
        from database import Base
        
        # Создаем движок для тестовой базы данных
        test_engine = create_engine(f"sqlite:///{test_db_path}", connect_args={"check_same_thread": False})
        
        # Создаем все таблицы
        print("📋 Создаем таблицы...")
        Base.metadata.create_all(bind=test_engine)
        
        # Проверяем созданные таблицы
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        
        # Получаем список всех таблиц
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]
        print(f"📋 Созданные таблицы: {table_names}")
        
        # Проверяем структуру таблицы users
        if 'users' in table_names:
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
            
            missing_columns = [col for col in required_columns if col not in column_names]
            
            if missing_columns:
                print(f"❌ Отсутствующие колонки в users: {missing_columns}")
            else:
                print("✅ Все необходимые колонки присутствуют в таблице users")
        else:
            print("❌ Таблица users не создана")
        
        # Проверяем таблицу tariffs
        if 'tariffs' in table_names:
            cursor.execute("PRAGMA table_info(tariffs);")
            tariff_columns = cursor.fetchall()
            tariff_column_names = [col[1] for col in tariff_columns]
            print(f"📋 Колонки в таблице tariffs: {tariff_column_names}")
            print("✅ Таблица tariffs создана")
        else:
            print("❌ Таблица tariffs не создана")
        
        # Проверяем таблицу workout_coefficients
        if 'workout_coefficients' in table_names:
            cursor.execute("PRAGMA table_info(workout_coefficients);")
            coeff_columns = cursor.fetchall()
            coeff_column_names = [col[1] for col in coeff_columns]
            print(f"📋 Колонки в таблице workout_coefficients: {coeff_column_names}")
            print("✅ Таблица workout_coefficients создана")
        else:
            print("❌ Таблица workout_coefficients не создана")
        
        conn.close()
        
        # Результат
        expected_tables = ['users', 'training_plans', 'workouts', 'workout_completion_marks', 'tariffs', 'workout_coefficients']
        missing_tables = [table for table in expected_tables if table not in table_names]
        
        print(f"\n🎯 Результат теста:")
        print(f"📊 Ожидаемые таблицы: {expected_tables}")
        print(f"📊 Созданные таблицы: {table_names}")
        
        if missing_tables:
            print(f"❌ Отсутствующие таблицы: {missing_tables}")
        else:
            print("✅ Все необходимые таблицы созданы")
        
        if not missing_tables and 'users' in table_names:
            print("✅ База данных готова для продакшена!")
        else:
            print("❌ Есть проблемы с созданием базы данных")
        
    except Exception as e:
        print(f"❌ Ошибка при создании базы данных: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Удаляем тестовую базу данных
        try:
            if os.path.exists(test_db_path):
                os.remove(test_db_path)
                print(f"🗑️ Удален тестовый файл: {test_db_path}")
        except:
            print(f"⚠️ Не удалось удалить тестовый файл: {test_db_path}")

if __name__ == "__main__":
    test_production_database()
