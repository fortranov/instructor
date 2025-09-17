#!/usr/bin/env python3
"""
Миграция 002: Исправление исключения среды в настройках предпочтительных дней
"""

import sqlite3
import os

# Метаданные миграции
version = "002_fix_wednesday_exclusion"
description = "Исправление исключения среды в настройках предпочтительных дней"
checksum = "b2c3d4e5f6g7"  # Можно использовать хеш содержимого миграции

def up():
    """Выполнить миграцию"""
    db_path = os.getenv("DB_PATH", "./triplan.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Обновить всех пользователей, у которых старое значение (без среды)
        print(f"  Обновление пользователей с исключением среды...")
        cursor.execute("""
            UPDATE users 
            SET preferred_workout_days = '[0,1,2,3,4,5,6]' 
            WHERE preferred_workout_days = '[0,1,2,4,5,6]'
        """)
        
        # Также обновить пользователей с NULL значениями
        cursor.execute("""
            UPDATE users 
            SET preferred_workout_days = '[0,1,2,3,4,5,6]' 
            WHERE preferred_workout_days IS NULL
        """)
        
        # Сохранить изменения
        conn.commit()
        
        # Проверить результат
        cursor.execute("SELECT COUNT(*) FROM users WHERE preferred_workout_days = '[0,1,2,3,4,5,6]'")
        updated_count = cursor.fetchone()[0]
        print(f"  Обновлено {updated_count} пользователей")
        
        # Проверить, остались ли пользователи со старым значением
        cursor.execute("SELECT COUNT(*) FROM users WHERE preferred_workout_days = '[0,1,2,4,5,6]'")
        old_count = cursor.fetchone()[0]
        if old_count > 0:
            print(f"  ⚠️ Осталось {old_count} пользователей со старым значением")
        else:
            print(f"  ✅ Все пользователи обновлены")
        
    finally:
        conn.close()

def down():
    """Откатить миграцию"""
    db_path = os.getenv("DB_PATH", "./triplan.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Вернуть старое значение (исключить среду)
        print(f"  Возврат к старому значению (исключение среды)...")
        cursor.execute("""
            UPDATE users 
            SET preferred_workout_days = '[0,1,2,4,5,6]' 
            WHERE preferred_workout_days = '[0,1,2,3,4,5,6]'
        """)
        
        conn.commit()
        print(f"  Пользователи возвращены к старому значению")
        
    finally:
        conn.close()
