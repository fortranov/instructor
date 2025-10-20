#!/usr/bin/env python3
"""
Скрипт миграции базы данных для исправления отсутствующих колонок
"""

import os
import sys
import sqlite3
from datetime import datetime
sys.path.append('.')

def check_and_migrate_database():
    """Проверить и мигрировать базу данных"""
    
    # Получаем путь к базе данных
    DB_PATH = os.getenv("DB_PATH", "./triplan.db")
    
    print(f"Проверка базы данных: {DB_PATH}")
    
    if not os.path.exists(DB_PATH):
        print("База данных не существует, будет создана при первом запуске приложения")
        return
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Проверяем существование таблицы users
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
        if not cursor.fetchone():
            print("Таблица users не найдена, будет создана при первом запуске приложения")
            conn.close()
            return
        
        # Получаем информацию о колонках таблицы users
        cursor.execute("PRAGMA table_info(users);")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print(f"Найденные колонки в таблице users: {column_names}")
        
        # Проверяем наличие необходимых колонок
        missing_columns = []
        
        if 'competition_date' not in column_names:
            missing_columns.append(('competition_date', 'DATE'))
            
        if 'competition_type' not in column_names:
            missing_columns.append(('competition_type', 'VARCHAR'))
        
        if missing_columns:
            print(f"Найдены отсутствующие колонки: {[col[0] for col in missing_columns]}")
            
            # Создаем резервную копию
            backup_path = f"{DB_PATH}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            print(f"Создаем резервную копию: {backup_path}")
            
            import shutil
            shutil.copy2(DB_PATH, backup_path)
            
            # Добавляем отсутствующие колонки
            for column_name, column_type in missing_columns:
                print(f"Добавляем колонку {column_name} ({column_type})")
                try:
                    cursor.execute(f"ALTER TABLE users ADD COLUMN {column_name} {column_type};")
                    print(f"✅ Колонка {column_name} добавлена успешно")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" in str(e).lower():
                        print(f"⚠️  Колонка {column_name} уже существует")
                    else:
                        print(f"❌ Ошибка при добавлении колонки {column_name}: {e}")
                        raise
            
            conn.commit()
            print("✅ Миграция завершена успешно")
            
        else:
            print("✅ Все необходимые колонки присутствуют")
        
        # Проверяем финальную структуру
        cursor.execute("PRAGMA table_info(users);")
        final_columns = cursor.fetchall()
        print("\nФинальная структура таблицы users:")
        for col in final_columns:
            print(f"  {col[1]} ({col[2]}) - nullable: {not col[3]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Ошибка при миграции базы данных: {e}")
        import traceback
        traceback.print_exc()
        raise

def recreate_database_from_scratch():
    """Пересоздать базу данных с нуля (для крайних случаев)"""
    
    DB_PATH = os.getenv("DB_PATH", "./triplan.db")
    
    print(f"⚠️  ВНИМАНИЕ: Пересоздание базы данных {DB_PATH}")
    print("Все данные будут потеряны!")
    
    # Создаем резервную копию если база существует
    if os.path.exists(DB_PATH):
        backup_path = f"{DB_PATH}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print(f"Создаем резервную копию: {backup_path}")
        
        import shutil
        shutil.copy2(DB_PATH, backup_path)
        
        # Удаляем старую базу
        os.remove(DB_PATH)
        print("Старая база данных удалена")
    
    # Создаем новую базу данных
    print("Создаем новую базу данных...")
    from database import create_tables
    create_tables()
    print("✅ Новая база данных создана")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Миграция базы данных Triplan')
    parser.add_argument('--recreate', action='store_true', 
                       help='Пересоздать базу данных с нуля (УДАЛИТ ВСЕ ДАННЫЕ)')
    
    args = parser.parse_args()
    
    if args.recreate:
        recreate_database_from_scratch()
    else:
        check_and_migrate_database()
