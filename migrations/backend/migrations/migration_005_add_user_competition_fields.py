"""
Миграция 005: Добавление полей соревнования в таблицу пользователей
"""

import sqlite3
import os

# Метаданные миграции
version = "005_add_user_competition_fields"
description = "Добавление полей соревнования в таблицу пользователей"

def up():
    """Добавляем поля для хранения информации о соревновании пользователя"""
    
    # Получаем путь к базе данных
    db_path = os.getenv("DB_PATH", "../../triplan.db")
    
    # Подключаемся к базе данных
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Проверяем существующие поля
        cursor.execute("PRAGMA table_info(users)")
        existing_columns = [col[1] for col in cursor.fetchall()]
        
        # Добавляем поле для даты соревнования если его нет
        if 'competition_date' not in existing_columns:
            cursor.execute("ALTER TABLE users ADD COLUMN competition_date DATE")
            print("✅ Добавлено поле competition_date")
        else:
            print("ℹ️  Поле competition_date уже существует")
        
        # Добавляем поле для типа соревнования если его нет
        if 'competition_type' not in existing_columns:
            cursor.execute("ALTER TABLE users ADD COLUMN competition_type VARCHAR")
            print("✅ Добавлено поле competition_type")
        else:
            print("ℹ️  Поле competition_type уже существует")
        
        conn.commit()
        print("✅ Миграция 005: Поля соревнований готовы")
        
    finally:
        conn.close()

def down():
    """Откат миграции - удаляем добавленные поля"""
    
    # SQLite не поддерживает DROP COLUMN, поэтому создаем новую таблицу без этих полей
    # Но для простоты оставим поля, так как они не мешают работе
    print("⚠️  Откат миграции 005: SQLite не поддерживает удаление столбцов, поля остаются")
