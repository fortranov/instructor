#!/usr/bin/env python3
"""
Миграция 001: Добавление поля preferred_workout_days в таблицу users
"""

import sqlite3
import os

# Метаданные миграции
version = "001_add_preferred_workout_days"
description = "Добавление поля preferred_workout_days в таблицу users"
checksum = "a1b2c3d4e5f6"  # Можно использовать хеш содержимого миграции

def up():
    """Выполнить миграцию"""
    db_path = os.getenv("DB_PATH", "../../triplan.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Проверить, существует ли уже поле
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'preferred_workout_days' in columns:
            print(f"  Поле preferred_workout_days уже существует в таблице users")
            return
        
        # Добавить поле preferred_workout_days
        print(f"  Добавление поля preferred_workout_days в таблицу users...")
        cursor.execute("""
            ALTER TABLE users 
            ADD COLUMN preferred_workout_days TEXT DEFAULT '[0,1,2,3,4,5,6]'
        """)
        
        # Обновить существующих пользователей значением по умолчанию
        cursor.execute("""
            UPDATE users 
            SET preferred_workout_days = '[0,1,2,3,4,5,6]' 
            WHERE preferred_workout_days IS NULL
        """)
        
        # Сохранить изменения
        conn.commit()
        
        # Проверить результат
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"  Обновлено {user_count} пользователей")
        
    finally:
        conn.close()

def down():
    """Откатить миграцию"""
    db_path = os.getenv("DB_PATH", "../../triplan.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # SQLite не поддерживает DROP COLUMN напрямую
        # Нужно пересоздать таблицу без этого поля
        
        # Создать временную таблицу с нужной структурой
        cursor.execute("""
            CREATE TABLE users_backup (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uin VARCHAR UNIQUE NOT NULL,
                email VARCHAR UNIQUE NOT NULL,
                hashed_password VARCHAR NOT NULL,
                first_name VARCHAR,
                last_name VARCHAR,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Скопировать данные (исключая preferred_workout_days)
        cursor.execute("""
            INSERT INTO users_backup 
            (id, uin, email, hashed_password, first_name, last_name, is_active, created_at, updated_at)
            SELECT id, uin, email, hashed_password, first_name, last_name, is_active, created_at, updated_at
            FROM users
        """)
        
        # Удалить старую таблицу
        cursor.execute("DROP TABLE users")
        
        # Переименовать временную таблицу
        cursor.execute("ALTER TABLE users_backup RENAME TO users")
        
        # Восстановить индексы
        cursor.execute("CREATE UNIQUE INDEX ix_users_uin ON users (uin)")
        cursor.execute("CREATE UNIQUE INDEX ix_users_email ON users (email)")
        
        conn.commit()
        print(f"  Поле preferred_workout_days удалено из таблицы users")
        
    finally:
        conn.close()
