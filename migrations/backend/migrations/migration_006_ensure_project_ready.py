"""
Миграция 006: Обеспечение готовности проекта к запуску
"""

import sqlite3
import os

# Метаданные миграции
version = "006_ensure_project_ready"
description = "Обеспечение готовности проекта к запуску"

def up():
    """Убеждаемся, что все необходимые таблицы и поля существуют для запуска проекта"""
    
    # Получаем путь к базе данных
    db_path = os.getenv("DB_PATH", "../../triplan.db")
    
    # Подключаемся к базе данных
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Получаем список существующих таблиц
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [row[0] for row in cursor.fetchall()]
    
        print("🔍 Проверяем готовность базы данных для запуска проекта...")
        
        # Проверяем наличие всех необходимых таблиц
        required_tables = ['users', 'training_plans', 'workouts', 'workout_completion_marks']
        missing_tables = [table for table in required_tables if table not in existing_tables]
        
        if missing_tables:
            print(f"⚠️  Отсутствуют таблицы: {missing_tables}")
            print("🔧 Создаем недостающие таблицы...")
            
            # Создаем базовые таблицы если их нет
            if 'users' not in existing_tables:
                cursor.execute("""
                    CREATE TABLE users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        uin VARCHAR UNIQUE,
                        email VARCHAR UNIQUE NOT NULL,
                        hashed_password VARCHAR NOT NULL,
                        first_name VARCHAR,
                        last_name VARCHAR,
                        is_active INTEGER DEFAULT 1,
                        preferred_workout_days VARCHAR DEFAULT '1,2,3,4,5,6,7',
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        competition_date DATE,
                        competition_type VARCHAR
                    )
                """)
                print("✅ Создана таблица users")
            
            if 'training_plans' not in existing_tables:
                cursor.execute("""
                    CREATE TABLE training_plans (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        complexity INTEGER NOT NULL,
                        competition_date DATE,
                        competition_type VARCHAR(17),
                        competition_distance FLOAT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                """)
                print("✅ Создана таблица training_plans")
            
            if 'workouts' not in existing_tables:
                cursor.execute("""
                    CREATE TABLE workouts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        plan_id INTEGER NOT NULL,
                        date DATE NOT NULL,
                        sport_type VARCHAR(8) NOT NULL,
                        duration_minutes INTEGER NOT NULL,
                        workout_type VARCHAR(9) NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (plan_id) REFERENCES training_plans (id)
                    )
                """)
                print("✅ Создана таблица workouts")
            
            if 'workout_completion_marks' not in existing_tables:
                cursor.execute("""
                    CREATE TABLE workout_completion_marks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        workout_id INTEGER NOT NULL,
                        user_id INTEGER NOT NULL,
                        date DATE NOT NULL,
                        completed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (workout_id) REFERENCES workouts (id),
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                """)
                print("✅ Создана таблица workout_completion_marks")
        
        # Проверяем наличие необходимых полей в таблице users
        if 'users' in existing_tables:
            cursor.execute("PRAGMA table_info(users)")
            user_columns = [col[1] for col in cursor.fetchall()]
            
            # Добавляем поля соревнований если их нет
            if 'competition_date' not in user_columns:
                cursor.execute("ALTER TABLE users ADD COLUMN competition_date DATE")
                print("✅ Добавлено поле competition_date в таблицу users")
            
            if 'competition_type' not in user_columns:
                cursor.execute("ALTER TABLE users ADD COLUMN competition_type VARCHAR")
                print("✅ Добавлено поле competition_type в таблицу users")
            
            # Добавляем поле предпочитаемых дней тренировок если его нет
            if 'preferred_workout_days' not in user_columns:
                cursor.execute("ALTER TABLE users ADD COLUMN preferred_workout_days VARCHAR DEFAULT '1,2,3,4,5,6,7'")
                print("✅ Добавлено поле preferred_workout_days в таблицу users")
        
        # Создаем индексы для производительности
        try:
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_training_plans_user_id ON training_plans(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_workouts_plan_id ON workouts(plan_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_workouts_date ON workouts(date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_workout_completion_marks_workout_id ON workout_completion_marks(workout_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_workout_completion_marks_user_id ON workout_completion_marks(user_id)")
            print("✅ Созданы индексы для оптимизации производительности")
        except Exception as e:
            print(f"⚠️  Предупреждение при создании индексов: {e}")
        
        # Сохраняем изменения
        conn.commit()
        print("🎉 База данных готова к запуску проекта!")
        
    finally:
        conn.close()

def down():
    """Откат миграции - удаляем созданные индексы"""
    
    # Получаем путь к базе данных
    db_path = os.getenv("DB_PATH", "../../triplan.db")
    
    # Подключаемся к базе данных
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("DROP INDEX IF EXISTS idx_users_email")
        cursor.execute("DROP INDEX IF EXISTS idx_training_plans_user_id")
        cursor.execute("DROP INDEX IF EXISTS idx_workouts_plan_id")
        cursor.execute("DROP INDEX IF EXISTS idx_workouts_date")
        cursor.execute("DROP INDEX IF EXISTS idx_workout_completion_marks_workout_id")
        cursor.execute("DROP INDEX IF EXISTS idx_workout_completion_marks_user_id")
        conn.commit()
        print("✅ Откат миграции 006: Удалены индексы")
    except Exception as e:
        print(f"⚠️  Предупреждение при откате миграции 006: {e}")
    finally:
        conn.close()
