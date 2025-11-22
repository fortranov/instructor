#!/usr/bin/env python3
"""
Скрипт миграции для добавления колонки is_custom в таблицу workouts
"""
import sqlite3
import os
import sys

# Определяем путь к базе данных
DB_PATH = os.getenv("DB_PATH", "./triplan.db")
# Если путь относительный, делаем его абсолютным относительно директории backend
if not os.path.isabs(DB_PATH):
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(backend_dir, DB_PATH)

def migrate():
    """Применить миграцию для добавления is_custom колонки"""
    print(f"Starting migration for database: {DB_PATH}")

    if not os.path.exists(DB_PATH):
        print(f"[ERROR] Database file not found: {DB_PATH}")
        return False

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Проверяем, существует ли таблица workouts
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='workouts';")
        if not cursor.fetchone():
            print("[ERROR] Workouts table does not exist")
            conn.close()
            return False

        # Получаем текущую схему таблицы workouts
        cursor.execute("PRAGMA table_info(workouts);")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]

        print(f"Current columns in workouts table: {column_names}")

        # Проверяем наличие поля is_custom
        if 'is_custom' in column_names:
            print("[OK] Column is_custom already exists in workouts table")
            conn.close()
            return True

        # Добавляем колонку is_custom
        print("Adding is_custom column to workouts table...")
        cursor.execute("ALTER TABLE workouts ADD COLUMN is_custom INTEGER DEFAULT 0;")
        conn.commit()

        # Проверяем, что колонка добавлена
        cursor.execute("PRAGMA table_info(workouts);")
        new_columns = cursor.fetchall()
        new_column_names = [col[1] for col in new_columns]

        if 'is_custom' in new_column_names:
            print("[OK] Successfully added is_custom column to workouts table")
            print(f"New columns: {new_column_names}")
            conn.close()
            return True
        else:
            print("[ERROR] Failed to add is_custom column")
            conn.close()
            return False

    except sqlite3.Error as e:
        print(f"[ERROR] SQLite error: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = migrate()
    sys.exit(0 if success else 1)
