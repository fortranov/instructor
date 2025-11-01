"""
Проверка структуры таблицы users
"""
import sqlite3

conn = sqlite3.connect("triplan.db")
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(users)")
columns = cursor.fetchall()

print("Struktura tablicy users:")
print("-" * 60)
for col in columns:
    print(f"  {col[1]} ({col[2]}) - default: {col[4]}, nullable: {not col[3]}")

conn.close()
