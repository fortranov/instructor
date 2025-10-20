"""
Скрипт для исправления структуры базы данных
"""

import sqlite3
import os

def fix_database():
    """Исправить структуру базы данных"""
    
    db_path = "./triplan.db"
    
    if not os.path.exists(db_path):
        print("База данных не найдена!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Проверяем текущую структуру таблицы users
        cursor.execute("PRAGMA table_info(users);")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print(f"Текущие колонки в таблице users: {column_names}")
        
        # Проверяем наличие колонки tariff_id
        if 'tariff_id' not in column_names:
            print("Добавляем колонку tariff_id...")
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN tariff_id INTEGER")
                conn.commit()
                print("✅ Колонка tariff_id добавлена успешно")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e).lower():
                    print("✅ Колонка tariff_id уже существует")
                else:
                    print(f"❌ Ошибка при добавлении колонки: {e}")
                    raise
        else:
            print("✅ Колонка tariff_id уже существует")
        
        # Проверяем финальную структуру
        cursor.execute("PRAGMA table_info(users);")
        final_columns = cursor.fetchall()
        final_column_names = [col[1] for col in final_columns]
        
        print(f"Финальные колонки в таблице users: {final_column_names}")
        
        # Проверяем наличие таблицы tariffs
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
            
            # Добавляем тарифы по умолчанию
            cursor.execute("INSERT INTO tariffs (name, type, view_full_plan, view_two_weeks) VALUES (?, ?, ?, ?)", 
                          ("Тестовый", "test", 0, 1))
            cursor.execute("INSERT INTO tariffs (name, type, view_full_plan, view_two_weeks) VALUES (?, ?, ?, ?)", 
                          ("Пробный", "trial", 0, 1))
            cursor.execute("INSERT INTO tariffs (name, type, view_full_plan, view_two_weeks) VALUES (?, ?, ?, ?)", 
                          ("Про", "pro", 1, 1))
            
            conn.commit()
            print("✅ Таблица tariffs создана и заполнена")
        else:
            print("✅ Таблица tariffs уже существует")
        
        # Проверяем наличие таблицы workout_coefficients
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
            
            # Добавляем коэффициенты по умолчанию
            cursor.execute("""
                INSERT INTO workout_coefficients (
                    weekly_distance_beginner, weekly_distance_5_10, weekly_distance_10_30, 
                    weekly_distance_30_50, weekly_distance_50_plus,
                    pace_8_plus, pace_7_8, pace_6_7, pace_5_6, pace_4_5, pace_4_minus,
                    target_distance_5k, target_distance_10k, target_distance_21k, target_distance_42k,
                    time_preparation_base, time_preparation_weeks_optimal
                ) VALUES (10, 50, 100, 200, 300, 20, 50, 100, 150, 200, 300, 50, 100, 150, 250, 100, 16)
            """)
            
            conn.commit()
            print("✅ Таблица workout_coefficients создана и заполнена")
        else:
            print("✅ Таблица workout_coefficients уже существует")
        
        conn.close()
        print("✅ База данных успешно исправлена!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    fix_database()
