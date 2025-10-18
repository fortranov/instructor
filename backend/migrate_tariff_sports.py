"""
Скрипт миграции для добавления колонок видов спорта в таблицу tariffs
"""

import sqlite3
import os
from database import DB_PATH

def migrate_tariff_sports():
    """Добавить колонки для видов спорта в таблицу tariffs"""
    
    print(f"🔄 Миграция тарифов: добавление колонок видов спорта")
    print(f"📁 База данных: {os.path.abspath(DB_PATH)}")
    
    if not os.path.exists(DB_PATH):
        print("❌ База данных не найдена!")
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Получаем текущую структуру таблицы tariffs
        cursor.execute("PRAGMA table_info(tariffs);")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print(f"📋 Текущие колонки в таблице tariffs: {column_names}")
        
        # Определяем колонки, которые нужно добавить
        new_columns = {
            'allow_running': 'INTEGER DEFAULT 1',
            'allow_cycling': 'INTEGER DEFAULT 0',
            'allow_swimming': 'INTEGER DEFAULT 0',
            'allow_triathlon': 'INTEGER DEFAULT 0'
        }
        
        # Добавляем отсутствующие колонки
        added_columns = []
        for col_name, col_type in new_columns.items():
            if col_name not in column_names:
                try:
                    alter_sql = f"ALTER TABLE tariffs ADD COLUMN {col_name} {col_type};"
                    print(f"➕ Добавление колонки: {col_name}")
                    cursor.execute(alter_sql)
                    added_columns.append(col_name)
                    print(f"✅ Колонка {col_name} добавлена")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" in str(e).lower():
                        print(f"⚠️  Колонка {col_name} уже существует")
                    else:
                        raise
            else:
                print(f"✓ Колонка {col_name} уже существует")
        
        if added_columns:
            conn.commit()
            print(f"\n✅ Успешно добавлено колонок: {len(added_columns)}")
            
            # Обновляем существующие тарифы
            print("\n🔄 Обновление существующих тарифов...")
            
            # По умолчанию все тарифы имеют доступ только к бегу
            cursor.execute("""
                UPDATE tariffs 
                SET allow_running = 1, 
                    allow_cycling = 0, 
                    allow_swimming = 0, 
                    allow_triathlon = 0
                WHERE allow_running IS NULL
            """)
            
            # Для тарифа PRO включаем все виды спорта
            cursor.execute("""
                UPDATE tariffs 
                SET allow_running = 1, 
                    allow_cycling = 1, 
                    allow_swimming = 1, 
                    allow_triathlon = 1
                WHERE type = 'pro'
            """)
            
            conn.commit()
            print("✅ Существующие тарифы обновлены")
            print("   • Тестовый и Пробный: только Бег")
            print("   • Про: все виды спорта")
        else:
            print("\n✓ Все колонки уже существуют, миграция не требуется")
        
        # Проверяем финальную структуру
        cursor.execute("PRAGMA table_info(tariffs);")
        final_columns = cursor.fetchall()
        final_column_names = [col[1] for col in final_columns]
        
        print(f"\n📋 Финальные колонки в таблице tariffs:")
        for col_name in final_column_names:
            print(f"   • {col_name}")
        
        # Выводим информацию о тарифах
        print(f"\n📊 Текущие тарифы:")
        cursor.execute("""
            SELECT name, type, allow_running, allow_cycling, allow_swimming, allow_triathlon 
            FROM tariffs
        """)
        tariffs = cursor.fetchall()
        
        if tariffs:
            for tariff in tariffs:
                name, tariff_type, running, cycling, swimming, triathlon = tariff
                sports = []
                if running: sports.append('Бег')
                if cycling: sports.append('Велосипед')
                if swimming: sports.append('Плавание')
                if triathlon: sports.append('Триатлон')
                
                print(f"   • {name} ({tariff_type}): {', '.join(sports) if sports else 'нет доступных видов спорта'}")
        else:
            print("   ⚠️  Тарифы не найдены в базе данных")
        
        conn.close()
        
        print("\n🎉 Миграция успешно завершена!")
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка миграции: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    migrate_tariff_sports()

