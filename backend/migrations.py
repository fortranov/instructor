"""
Модуль для миграций базы данных
"""

from sqlalchemy import text
from database import engine, Base
import logging

logger = logging.getLogger(__name__)

def run_migrations():
    """Выполнить миграции базы данных"""
    migrations = [
        {
            "name": "add_user_competition_fields",
            "description": "Добавить поля competition_date и competition_type в таблицу users",
            "sql": [
                "ALTER TABLE users ADD COLUMN competition_date DATE",
                "ALTER TABLE users ADD COLUMN competition_type VARCHAR"
            ],
            "check_sql": "SELECT name FROM pragma_table_info('users') WHERE name IN ('competition_date', 'competition_type')"
        }
        # Здесь можно добавить будущие миграции
    ]
    
    with engine.connect() as conn:
        try:
            for migration in migrations:
                logger.info(f"Running migration: {migration['name']}")
                
                # Проверяем, нужно ли выполнять миграцию
                result = conn.execute(text(migration["check_sql"])).fetchall()
                existing_columns = [row[0] for row in result]
                
                if len(existing_columns) == 2:  # Обе колонки уже существуют
                    logger.info(f"Migration {migration['name']} already applied, skipping")
                    continue
                
                # Выполняем SQL команды миграции
                for sql in migration["sql"]:
                    try:
                        conn.execute(text(sql))
                        logger.info(f"Executed: {sql}")
                    except Exception as e:
                        logger.warning(f"Error executing {sql}: {e}")
                        # Продолжаем выполнение других команд
                
                conn.commit()
                logger.info(f"Migration {migration['name']} completed successfully")
                
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

def check_database_schema():
    """Проверить схему базы данных"""
    from sqlalchemy import inspect
    
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    schema_info = {}
    for table in tables:
        columns = [col['name'] for col in inspector.get_columns(table)]
        schema_info[table] = columns
    
    return schema_info

if __name__ == "__main__":
    # Запуск миграций из командной строки
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        print("Database schema:")
        schema = check_database_schema()
        for table, columns in schema.items():
            print(f"  {table}: {columns}")
    else:
        print("Running database migrations...")
        run_migrations()
        print("Migrations completed!")
