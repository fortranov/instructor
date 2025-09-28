#!/usr/bin/env python3
"""
Тестирование сценария продакшена - создание базы данных с нуля
"""

import os
import sys
import tempfile
import shutil
sys.path.append('.')

def test_production_scenario():
    """Тестировать сценарий создания базы данных с нуля в продакшене"""
    
    # Создаем временную директорию для тестирования
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_db_path = os.path.join(temp_dir, "triplan.db")
        
        print(f"Testing production scenario with database: {temp_db_path}")
        
        # Устанавливаем переменную окружения
        original_db_path = os.environ.get("DB_PATH")
        os.environ["DB_PATH"] = temp_db_path
        
        try:
            # Импортируем модули заново с новым путем к БД
            import importlib
            import database
            importlib.reload(database)
            
            # Тестируем процесс инициализации
            print("\n=== STEP 1: Database compatibility check ===")
            database.ensure_database_compatibility()
            
            print("\n=== STEP 2: Create tables ===")
            database.create_tables()
            
            print("\n=== STEP 3: Test user creation ===")
            from auth import create_user
            from database import SessionLocal
            
            db = SessionLocal()
            try:
                test_user = create_user(
                    db=db,
                    email="production_test@example.com",
                    password="testpassword123",
                    first_name="Production",
                    last_name="Test"
                )
                print(f"✅ User created successfully: {test_user.email}")
                print(f"Competition date: {test_user.competition_date}")
                print(f"Competition type: {test_user.competition_type}")
                
                # Тестируем запрос, который вызывал ошибку
                print("\n=== STEP 4: Test problematic query ===")
                from database import User
                user_query = db.query(User).filter(User.email == 'production_test@example.com').first()
                
                if user_query:
                    print(f"✅ Query successful: {user_query.email}")
                    print(f"Competition date: {user_query.competition_date}")
                    print(f"Competition type: {user_query.competition_type}")
                else:
                    print("❌ User not found in query")
                
            except Exception as e:
                print(f"❌ Error during user operations: {e}")
                import traceback
                traceback.print_exc()
                raise
            finally:
                db.close()
            
            print("\n=== STEP 5: Verify database schema ===")
            import sqlite3
            conn = sqlite3.connect(temp_db_path)
            cursor = conn.cursor()
            
            cursor.execute("PRAGMA table_info(users);")
            columns = cursor.fetchall()
            
            print("Final database schema:")
            for col in columns:
                print(f"  {col[1]} ({col[2]}) - nullable: {not col[3]}")
            
            # Проверяем наличие критических колонок
            column_names = [col[1] for col in columns]
            required_columns = ['competition_date', 'competition_type']
            
            for col_name in required_columns:
                if col_name in column_names:
                    print(f"✅ Column {col_name} is present")
                else:
                    print(f"❌ Column {col_name} is MISSING")
                    raise Exception(f"Critical column {col_name} is missing!")
            
            conn.close()
            
            print("\n🎉 Production scenario test PASSED!")
            
        finally:
            # Восстанавливаем оригинальную переменную окружения
            if original_db_path:
                os.environ["DB_PATH"] = original_db_path
            else:
                os.environ.pop("DB_PATH", None)

if __name__ == "__main__":
    test_production_scenario()
