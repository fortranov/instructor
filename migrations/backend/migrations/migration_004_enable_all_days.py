#!/usr/bin/env python3
"""
Миграция 004: Включить все дни недели по умолчанию
Обновляет всех пользователей, чтобы по умолчанию были доступны все дни недели
"""

import os
import sqlite3

# Метаданные миграции
version = "004_enable_all_days"
description = "Включить все дни недели по умолчанию - обновление на [0,1,2,3,4,5,6]"
checksum = "004_enable_all_days_2024"

def up():
    """Выполнить миграцию"""
    db_path = os.getenv("DB_PATH", "../triplan.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print(f"🔄 Выполнение миграции {version}: {description}")
        
        # Обновить всех пользователей на все дни недели
        cursor.execute("""
            UPDATE users 
            SET preferred_workout_days = '[0,1,2,3,4,5,6]' 
            WHERE preferred_workout_days = '[0,1,4,5,6]' OR 
                  preferred_workout_days = '[0,1,2,4,5,6]' OR 
                  preferred_workout_days = '[0,1,2,3,4,5,6]' OR 
                  preferred_workout_days IS NULL
        """)
        
        updated_count = cursor.rowcount
        print(f"  📊 Обновлено пользователей: {updated_count}")
        
        # Проверить результат
        cursor.execute("SELECT COUNT(*) FROM users WHERE preferred_workout_days = '[0,1,2,3,4,5,6]'")
        all_days_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        print(f"  ✅ Пользователей с всеми днями: {all_days_count}/{total_users}")
        
        if all_days_count == total_users:
            print(f"  ✅ Все пользователи обновлены на все дни недели [0,1,2,3,4,5,6]")
        else:
            print(f"  ⚠️  Не все пользователи обновлены. Проверьте данные.")
        
        conn.commit()
        print(f"  ✅ Миграция {version} выполнена успешно")
        
    except Exception as e:
        conn.rollback()
        print(f"  ❌ Ошибка при выполнении миграции {version}: {e}")
        raise
    finally:
        conn.close()

def down():
    """Откатить миграцию"""
    db_path = os.getenv("DB_PATH", "../triplan.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print(f"⏪ Откат миграции {version}")
        
        # Вернуть к предыдущему состоянию (исключить среду и четверг)
        cursor.execute("""
            UPDATE users 
            SET preferred_workout_days = '[0,1,4,5,6]' 
            WHERE preferred_workout_days = '[0,1,2,3,4,5,6]'
        """)
        
        updated_count = cursor.rowcount
        print(f"  📊 Откачено пользователей: {updated_count}")
        
        conn.commit()
        print(f"  ✅ Откат миграции {version} выполнен успешно")
        
    except Exception as e:
        conn.rollback()
        print(f"  ❌ Ошибка при откате миграции {version}: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "down":
        down()
    else:
        up()
