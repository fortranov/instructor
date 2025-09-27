#!/usr/bin/env python3
"""
Универсальный скрипт для запуска миграций базы данных
"""

import os
import sys
import logging
from datetime import datetime
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import OperationalError

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class DatabaseMigrator:
    """Класс для выполнения миграций базы данных"""
    
    def __init__(self, database_url: str):
        """
        Инициализация мигратора
        
        Args:
            database_url: URL базы данных (например, sqlite:///./triplan.db)
        """
        self.database_url = database_url
        self.engine = create_engine(database_url, echo=False)
        
    def get_current_schema(self):
        """Получить текущую схему базы данных"""
        inspector = inspect(self.engine)
        schema_info = {}
        
        for table_name in inspector.get_table_names():
            columns = [col['name'] for col in inspector.get_columns(table_name)]
            schema_info[table_name] = columns
            
        return schema_info
    
    def check_column_exists(self, table_name: str, column_name: str) -> bool:
        """Проверить существование колонки в таблице"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(
                    f"SELECT name FROM pragma_table_info('{table_name}') WHERE name = '{column_name}'"
                )).fetchone()
                return result is not None
        except Exception as e:
            logger.warning(f"Error checking column {table_name}.{column_name}: {e}")
            return False
    
    def add_column(self, table_name: str, column_name: str, column_type: str, nullable: bool = True):
        """Добавить колонку в таблицу"""
        if self.check_column_exists(table_name, column_name):
            logger.info(f"Column {table_name}.{column_name} already exists, skipping")
            return True
            
        try:
            with self.engine.connect() as conn:
                nullable_clause = "" if nullable else " NOT NULL"
                sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}{nullable_clause}"
                conn.execute(text(sql))
                conn.commit()
                logger.info(f"Added column {table_name}.{column_name}")
                return True
        except Exception as e:
            logger.error(f"Failed to add column {table_name}.{column_name}: {e}")
            return False
    
    def run_migration(self, migration_name: str, migration_func):
        """Выполнить миграцию"""
        logger.info(f"Running migration: {migration_name}")
        
        try:
            success = migration_func(self)
            if success:
                logger.info(f"Migration {migration_name} completed successfully")
            else:
                logger.error(f"Migration {migration_name} failed")
            return success
        except Exception as e:
            logger.error(f"Migration {migration_name} failed with exception: {e}")
            return False
    
    def create_tables_if_not_exist(self):
        """Создать основные таблицы если они не существуют"""
        try:
            # Импортируем модуль database из backend
            backend_path = os.path.join(os.path.dirname(__file__), 'backend')
            if os.path.exists(backend_path):
                sys.path.append(backend_path)
            
            from database import create_tables
            create_tables()
            logger.info("Database tables created/verified")
            return True
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            return False
    
    def run_all_migrations(self):
        """Выполнить все миграции"""
        logger.info("Starting database migrations...")
        
        # Создаем таблицы если их нет
        if not self.create_tables_if_not_exist():
            logger.error("Failed to create database tables")
            return False
        
        # Получаем текущую схему
        current_schema = self.get_current_schema()
        logger.info(f"Current database schema: {current_schema}")
        
        # Список миграций
        migrations = [
            ("add_user_competition_fields", self.migration_add_user_competition_fields),
            # Здесь можно добавить новые миграции
        ]
        
        success_count = 0
        total_migrations = len(migrations)
        
        for migration_name, migration_func in migrations:
            if self.run_migration(migration_name, migration_func):
                success_count += 1
        
        logger.info(f"Migrations completed: {success_count}/{total_migrations} successful")
        return success_count == total_migrations
    
    def migration_add_user_competition_fields(self, migrator):
        """Миграция: добавление полей competition_date и competition_type в таблицу users"""
        success = True
        
        # Добавляем поле competition_date
        if not migrator.add_column("users", "competition_date", "DATE", nullable=True):
            success = False
            
        # Добавляем поле competition_type
        if not migrator.add_column("users", "competition_type", "VARCHAR", nullable=True):
            success = False
            
        return success

def main():
    """Основная функция"""
    # Получение URL базы данных из переменной окружения
    database_url = os.getenv("DATABASE_URL", "sqlite:///./triplan.db")
    
    # Проверка наличия файла базы данных для SQLite
    if database_url.startswith("sqlite:///"):
        db_path = database_url.replace("sqlite:///", "")
        if not os.path.exists(db_path):
            logger.warning(f"Database file {db_path} does not exist. It will be created.")
    
    logger.info(f"Using database: {database_url}")
    
    # Создание мигратора
    migrator = DatabaseMigrator(database_url)
    
    # Выполнение миграций
    try:
        success = migrator.run_all_migrations()
        
        if success:
            logger.info("All migrations completed successfully!")
            # Показываем итоговую схему
            final_schema = migrator.get_current_schema()
            logger.info(f"Final database schema: {final_schema}")
            sys.exit(0)
        else:
            logger.error("Some migrations failed!")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Migration process failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
