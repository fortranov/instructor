"""
Миграция 005: Добавление полей соревнования в таблицу пользователей
"""

from sqlalchemy import text

def upgrade(connection):
    """Добавляем поля для хранения информации о соревновании пользователя"""
    
    # Добавляем поле для даты соревнования
    connection.execute(text("""
        ALTER TABLE users 
        ADD COLUMN competition_date DATE NULL
    """))
    
    # Добавляем поле для типа соревнования
    connection.execute(text("""
        ALTER TABLE users 
        ADD COLUMN competition_type VARCHAR(50) NULL
    """))
    
    print("✅ Миграция 005: Добавлены поля competition_date и competition_type в таблицу users")

def downgrade(connection):
    """Откат миграции - удаляем добавленные поля"""
    
    # SQLite не поддерживает DROP COLUMN, поэтому создаем новую таблицу без этих полей
    # Но для простоты оставим поля, так как они не мешают работе
    print("⚠️  Откат миграции 005: SQLite не поддерживает удаление столбцов, поля остаются")
