"""
Скрипт для проверки схемы базы данных

Использование:
    python check_database_schema.py                    # Локальная база данных
    python check_database_schema.py /path/to/triplan.db # Кастомный путь
"""
import sqlite3
import sys
import os

def check_database_schema(db_path):
    """Проверяет структуру базы данных и наличие необходимых полей"""

    if not os.path.exists(db_path):
        print(f"[ERROR] Baza dannyh ne najdena: {db_path}")
        return False

    print(f"Proverka bazy dannyh: {db_path}")
    print("=" * 70)

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Проверяем структуру таблицы users
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]

        print("\n[1] STRUKTURA TABLICY 'users':")
        print("-" * 70)
        for col in columns:
            print(f"   {col[1]:30} {col[2]:15} {'(NOT NULL)' if col[3] else ''}")

        # Проверяем критичные поля
        required_fields = {
            'has_strength_training': 'INTEGER',
            'preferred_workout_days': 'VARCHAR',
        }

        print("\n[2] PROVERKA NEOBHODIMYH POLEJ:")
        print("-" * 70)
        all_fields_present = True

        for field_name, expected_type in required_fields.items():
            if field_name in column_names:
                print(f"   [OK] {field_name:30} - prisutstvuet")
            else:
                print(f"   [MISSING] {field_name:30} - OTSUTSTVUET!")
                all_fields_present = False

        # Проверяем SportType.STRENGTH в workouts
        cursor.execute("SELECT DISTINCT sport_type FROM workouts")
        sport_types = [row[0] for row in cursor.fetchall()]

        print("\n[3] TIPY SPORTA V TRENIROVKAH:")
        print("-" * 70)
        for sport in sport_types:
            print(f"   - {sport}")

        # Проверяем наличие strength в любом регистре
        has_strength = any('strength' in s.lower() for s in sport_types)
        if has_strength:
            cursor.execute("SELECT COUNT(*) FROM workouts WHERE LOWER(sport_type) = 'strength'")
            strength_count = cursor.fetchone()[0]
            print(f"\n   [OK] Silovye trenirovki v baze: {strength_count}")
        else:
            print("\n   [WARNING] Net silovyh trenirovok v baze dannyh")

        # Проверяем значения has_strength_training
        if 'has_strength_training' in column_names:
            cursor.execute("SELECT email, has_strength_training FROM users")
            users = cursor.fetchall()

            print("\n[4] NASTROJKI POL'ZOVATELEJ:")
            print("-" * 70)
            for user in users:
                status = "[ON] Vklyucheno" if user[1] == 1 else "[OFF] Vyklyucheno"
                print(f"   {user[0]:40} {status}")

        conn.close()

        # Итоговый вывод
        print("\n" + "=" * 70)
        if all_fields_present:
            print("[SUCCESS] BAZA DANNYH GOTOVA K RABOTE")
            print("\nVse neobhodimye polya prisutstvuyut.")
            return True
        else:
            print("[WARNING] TREBUETSYA MIGRACIYA!")
            print("\nDlya migracii vypolnite:")
            print(f"  python migrate_add_strength_training.py {db_path}")
            return False

    except Exception as e:
        print(f"\n[ERROR] Oshibka pri proverke bazy dannyh: {e}")
        import traceback
        traceback.print_exc()
        if 'conn' in locals():
            conn.close()
        return False

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("PROVERKA SHEMY BAZY DANNYH TRIPLAN")
    print("=" * 70 + "\n")

    # Определяем путь к базе данных
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        db_path = os.getenv("DB_PATH", "./triplan.db")

    success = check_database_schema(db_path)

    print("\n" + "=" * 70 + "\n")

    if success:
        sys.exit(0)
    else:
        sys.exit(1)
