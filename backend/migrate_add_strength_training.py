"""
Миграция для добавления поля has_strength_training в таблицу users

Использование:
    python migrate_add_strength_training.py                    # Локальная разработка
    python migrate_add_strength_training.py /path/to/triplan.db # Кастомный путь
"""
import sqlite3
import sys
import os

def migrate_database(db_path):
    """Добавляет поле has_strength_training в таблицу users"""

    # Проверяем существование файла базы данных
    if not os.path.exists(db_path):
        print(f"  [WARNING] Baza dannyh ne najdena: {db_path}")
        return False

    print(f"Migraciya bazy dannyh: {db_path}")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Проверяем, существует ли уже поле
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'has_strength_training' in columns:
            print(f"  [OK] Pole has_strength_training uzhe sushhestvuet")
            conn.close()
            return True

        # Добавляем новое поле
        cursor.execute("""
            ALTER TABLE users
            ADD COLUMN has_strength_training INTEGER DEFAULT 0
        """)
        conn.commit()
        print(f"  [SUCCESS] Pole has_strength_training uspeshno dobavleno")

        # Проверяем результат
        cursor.execute("PRAGMA table_info(users)")
        columns_after = [column[1] for column in cursor.fetchall()]

        if 'has_strength_training' in columns_after:
            print(f"  [VERIFIED] Migraciya primenyena uspeshno")
            conn.close()
            return True
        else:
            print(f"  [ERROR] Pole ne dobavleno posle migracii")
            conn.close()
            return False

    except Exception as e:
        print(f"  [ERROR] Oshibka pri migracii: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("MIGRACIYA: Dobavlenie has_strength_training v tablicu users")
    print("=" * 70)
    print()

    # Если указан путь к базе данных как аргумент
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
        success = migrate_database(db_path)

        if success:
            print("\n[SUCCESS] Migraciya zavershena uspeshno!")
            print("\nNE ZABUD'TE:")
            print("  1. Perezapustit' backend server")
            print("  2. Proverit' rabotu prilozheniya")
            sys.exit(0)
        else:
            print("\n[ERROR] Migraciya ne udalas'!")
            sys.exit(1)
    else:
        # Локальная разработка - мигрируем обе базы
        print("Rezhim razrabotki: migraciya lokal'nyh baz dannyh\n")

        results = []
        for db_name in ["triplan.db", "test_fresh.db"]:
            results.append(migrate_database(db_name))
            print()

        if any(results):
            print("[SUCCESS] Migraciya zavershena!")
            print("\nNE ZABUD'TE perezapustit' backend server!")
            sys.exit(0)
        else:
            print("[WARNING] Ni odna baza dannyh ne byla migrirovana")
            sys.exit(0)
