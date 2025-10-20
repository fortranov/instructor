"""
Миграция для добавления админских таблиц и колонок
"""

import sqlite3
import os
from database import DB_PATH

def migrate_database():
    """Выполнить миграцию базы данных для админских функций"""
    
    print(f"Выполняем миграцию базы данных: {DB_PATH}")
    
    if not os.path.exists(DB_PATH):
        print("База данных не существует. Создайте её сначала.")
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Проверяем существование колонки tariff_id в таблице users
        cursor.execute("PRAGMA table_info(users);")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'tariff_id' not in column_names:
            print("Добавляем колонку tariff_id в таблицу users...")
            cursor.execute("ALTER TABLE users ADD COLUMN tariff_id INTEGER;")
            print("✅ Колонка tariff_id добавлена")
        else:
            print("✅ Колонка tariff_id уже существует")
        
        # Проверяем существование таблицы tariffs
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tariffs';")
        if not cursor.fetchone():
            print("Создаем таблицу tariffs...")
            cursor.execute("""
                CREATE TABLE tariffs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR NOT NULL,
                    type VARCHAR NOT NULL UNIQUE,
                    view_full_plan INTEGER DEFAULT 0,
                    view_two_weeks INTEGER DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            """)
            print("✅ Таблица tariffs создана")
        else:
            print("✅ Таблица tariffs уже существует")
        
        # Проверяем существование таблицы workout_coefficients
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='workout_coefficients';")
        if not cursor.fetchone():
            print("Создаем таблицу workout_coefficients...")
            cursor.execute("""
                CREATE TABLE workout_coefficients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    weekly_distance_beginner INTEGER DEFAULT 10,
                    weekly_distance_5_10 INTEGER DEFAULT 50,
                    weekly_distance_10_30 INTEGER DEFAULT 100,
                    weekly_distance_30_50 INTEGER DEFAULT 200,
                    weekly_distance_50_plus INTEGER DEFAULT 300,
                    pace_8_plus INTEGER DEFAULT 20,
                    pace_7_8 INTEGER DEFAULT 50,
                    pace_6_7 INTEGER DEFAULT 100,
                    pace_5_6 INTEGER DEFAULT 150,
                    pace_4_5 INTEGER DEFAULT 200,
                    pace_4_minus INTEGER DEFAULT 300,
                    target_distance_5k INTEGER DEFAULT 50,
                    target_distance_10k INTEGER DEFAULT 100,
                    target_distance_21k INTEGER DEFAULT 150,
                    target_distance_42k INTEGER DEFAULT 250,
                    time_preparation_base INTEGER DEFAULT 100,
                    time_preparation_weeks_optimal INTEGER DEFAULT 16,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            """)
            print("✅ Таблица workout_coefficients создана")
        else:
            print("✅ Таблица workout_coefficients уже существует")
        
        conn.commit()
        conn.close()
        
        print("✅ Миграция завершена успешно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при выполнении миграции: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    migrate_database()
