#!/usr/bin/env python3
"""
Миграция 003: Правильное исправление исключения среды в настройках предпочтительных дней
"""

import sqlite3
import os

# Метаданные миграции
version = "003_fix_wednesday_exclusion_correct"
description = "Правильное исправление исключения среды - обновление на [0,1,4,5,6]"
checksum = "c3d4e5f6g7h8"  # Можно использовать хеш содержимого миграции

def up():
    """Выполнить миграцию"""
    db_path = os.getenv("DB_PATH", "../../triplan.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Обновить всех пользователей, у которых старое значение (средой включена)
        print(f"  Обновление пользователей с включенной средой...")
        cursor.execute("""
            UPDATE users 
            SET preferred_workout_days = '[0,1,4,5,6]' 
            WHERE preferred_workout_days = '[0,1,2,4,5,6]'
        """)
        
        # Также обновить пользователей с новым значением (включающим среду) на правильное
        cursor.execute("""
            UPDATE users 
            SET preferred_workout_days = '[0,1,4,5,6]' 
            WHERE preferred_workout_days = '[0,1,2,3,4,5,6]'
        """)
        
        # Обновить пользователей с NULL значениями
        cursor.execute("""
            UPDATE users 
            SET preferred_workout_days = '[0,1,4,5,6]' 
            WHERE preferred_workout_days IS NULL
        """)
        
        # Сохранить изменения
        conn.commit()
        
        # Проверить результат
        cursor.execute("SELECT COUNT(*) FROM users WHERE preferred_workout_days = '[0,1,4,5,6]'")
        updated_count = cursor.fetchone()[0]
        print(f"  Обновлено {updated_count} пользователей")
        
        # Проверить, остались ли пользователи со старыми значениями
        cursor.execute("SELECT COUNT(*) FROM users WHERE preferred_workout_days = '[0,1,2,4,5,6]'")
        old_count = cursor.fetchone()[0]
        if old_count > 0:
            print(f"  ⚠️ Осталось {old_count} пользователей со старым значением [0,1,2,4,5,6]")
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE preferred_workout_days = '[0,1,2,3,4,5,6]'")
        new_count = cursor.fetchone()[0]
        if new_count > 0:
            print(f"  ⚠️ Осталось {new_count} пользователей со значением [0,1,2,3,4,5,6]")
        
        if old_count == 0 and new_count == 0:
            print(f"  ✅ Все пользователи обновлены на правильное значение [0,1,4,5,6]")
        
    finally:
        conn.close()

def down():
    """Откатить миграцию"""
    db_path = os.getenv("DB_PATH", "../../triplan.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Вернуть старое значение (включить среду)
        print(f"  Возврат к старому значению (включение среды)...")
        cursor.execute("""
            UPDATE users 
            SET preferred_workout_days = '[0,1,2,4,5,6]' 
            WHERE preferred_workout_days = '[0,1,4,5,6]'
        """)
        
        conn.commit()
        print(f"  Пользователи возвращены к старому значению")
        
    finally:
        conn.close()
