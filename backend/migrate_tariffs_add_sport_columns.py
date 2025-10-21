"""
Миграция для добавления колонок видов спорта в таблицу tariffs
"""

import sqlite3
import os

def migrate_tariffs_table():
    """Добавить колонки allow_running, allow_cycling, allow_swimming, allow_triathlon в таблицу tariffs"""

    db_path = os.getenv("DB_PATH", "./triplan.db")
    print(f"Миграция БД: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Проверяем текущую структуру таблицы
        cursor.execute("PRAGMA table_info(tariffs)")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"Текущие колонки в tariffs: {columns}")

        # Колонки, которые нужно добавить
        new_columns = {
            'allow_running': 'INTEGER DEFAULT 1',
            'allow_cycling': 'INTEGER DEFAULT 0',
            'allow_swimming': 'INTEGER DEFAULT 0',
            'allow_triathlon': 'INTEGER DEFAULT 0'
        }

        # Добавляем только отсутствующие колонки
        for column_name, column_def in new_columns.items():
            if column_name not in columns:
                print(f"Добавление колонки {column_name}...")
                cursor.execute(f"ALTER TABLE tariffs ADD COLUMN {column_name} {column_def}")
                print(f"✓ Колонка {column_name} добавлена")
            else:
                print(f"✓ Колонка {column_name} уже существует")

        conn.commit()

        # Проверяем новую структуру
        cursor.execute("PRAGMA table_info(tariffs)")
        columns_after = [row[1] for row in cursor.fetchall()]
        print(f"\nКолонки после миграции: {columns_after}")

        # Обновляем значения по умолчанию для существующих тарифов
        print("\nОбновление значений по умолчанию для существующих тарифов...")
        cursor.execute("""
            UPDATE tariffs
            SET allow_running = 1,
                allow_cycling = CASE
                    WHEN type = 'PRO' THEN 1
                    ELSE 0
                END,
                allow_swimming = CASE
                    WHEN type = 'PRO' THEN 1
                    ELSE 0
                END,
                allow_triathlon = CASE
                    WHEN type = 'PRO' THEN 1
                    ELSE 0
                END
            WHERE allow_running IS NULL OR allow_running = 0
        """)
        conn.commit()

        # Показываем текущие тарифы
        cursor.execute("SELECT id, name, type, allow_running, allow_cycling, allow_swimming, allow_triathlon FROM tariffs")
        tariffs = cursor.fetchall()
        print("\nТекущие тарифы:")
        for tariff in tariffs:
            print(f"  ID: {tariff[0]}, Название: {tariff[1]}, Тип: {tariff[2]}, "
                  f"Бег: {tariff[3]}, Велосипед: {tariff[4]}, Плавание: {tariff[5]}, Триатлон: {tariff[6]}")

        print("\n✅ Миграция успешно завершена!")

    except Exception as e:
        print(f"❌ Ошибка миграции: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_tariffs_table()
