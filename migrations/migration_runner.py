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
        
        # Сначала запускаем продвинутую систему миграций
        if not self.run_advanced_migrations():
            logger.error("Advanced migrations failed")
            return False
        
        # Создаем таблицы если их нет (для совместимости)
        if not self.create_tables_if_not_exist():
            logger.error("Failed to create database tables")
            return False
        
        # Получаем текущую схему
        current_schema = self.get_current_schema()
        logger.info(f"Current database schema: {current_schema}")
        
        # Список простых миграций (для совместимости)
        migrations = [
            ("add_user_competition_fields", self.migration_add_user_competition_fields),
            ("ensure_project_ready", self.migration_ensure_project_ready),
            # Здесь можно добавить новые миграции
        ]
        
        success_count = 0
        total_migrations = len(migrations)
        
        for migration_name, migration_func in migrations:
            if self.run_migration(migration_name, migration_func):
                success_count += 1
        
        logger.info(f"Simple migrations completed: {success_count}/{total_migrations} successful")
        return success_count == total_migrations
    
    def run_advanced_migrations(self):
        """Запустить продвинутую систему миграций"""
        try:
            logger.info("Running advanced migration system...")
            
            # Импортируем менеджер миграций
            backend_path = os.path.join(os.path.dirname(__file__), 'backend')
            if os.path.exists(backend_path):
                sys.path.append(backend_path)
            
            from migrations.migration_manager import MigrationManager
            
            # Извлекаем путь к базе данных
            if self.database_url.startswith("sqlite:///"):
                db_path = self.database_url.replace("sqlite:///", "")
            else:
                db_path = "triplan.db"  # fallback
            
            # Создаем менеджер миграций
            manager = MigrationManager(db_path)
            
            # Запускаем все ожидающие миграции
            success = manager.run_migrations()
            
            if success:
                logger.info("Advanced migrations completed successfully")
            else:
                logger.error("Some advanced migrations failed")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to run advanced migrations: {e}")
            return False
    
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
    
    def migration_ensure_project_ready(self, migrator):
        """Миграция: обеспечение готовности проекта к запуску"""
        success = True
        
        logger.info("🔍 Проверяем готовность базы данных для запуска проекта...")
        
        try:
            # Получаем текущую схему
            current_schema = migrator.get_current_schema()
            
            # Проверяем наличие всех необходимых таблиц
            required_tables = ['users', 'training_plans', 'workouts', 'workout_completion_marks']
            existing_tables = list(current_schema.keys())
            missing_tables = [table for table in required_tables if table not in existing_tables]
            
            if missing_tables:
                logger.warning(f"Отсутствуют таблицы: {missing_tables}")
                logger.info("Таблицы будут созданы автоматически при запуске приложения")
            
            # Проверяем наличие необходимых полей в таблице users
            if 'users' in existing_tables:
                user_columns = current_schema['users']
                
                # Добавляем поле предпочитаемых дней тренировок если его нет
                if 'preferred_workout_days' not in user_columns:
                    if not migrator.add_column("users", "preferred_workout_days", "VARCHAR", nullable=True):
                        success = False
                    else:
                        logger.info("✅ Добавлено поле preferred_workout_days в таблицу users")
                
                # Проверяем поля соревнований
                if 'competition_date' not in user_columns:
                    if not migrator.add_column("users", "competition_date", "DATE", nullable=True):
                        success = False
                    else:
                        logger.info("✅ Добавлено поле competition_date в таблицу users")
                
                if 'competition_type' not in user_columns:
                    if not migrator.add_column("users", "competition_type", "VARCHAR", nullable=True):
                        success = False
                    else:
                        logger.info("✅ Добавлено поле competition_type в таблицу users")
            
            # Создаем индексы для производительности
            try:
                with migrator.engine.connect() as conn:
                    conn.execute(text("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)"))
                    conn.execute(text("CREATE INDEX IF NOT EXISTS idx_training_plans_user_id ON training_plans(user_id)"))
                    conn.execute(text("CREATE INDEX IF NOT EXISTS idx_workouts_plan_id ON workouts(plan_id)"))
                    conn.execute(text("CREATE INDEX IF NOT EXISTS idx_workouts_date ON workouts(date)"))
                    conn.execute(text("CREATE INDEX IF NOT EXISTS idx_workout_completion_marks_workout_id ON workout_completion_marks(workout_id)"))
                    conn.execute(text("CREATE INDEX IF NOT EXISTS idx_workout_completion_marks_user_id ON workout_completion_marks(user_id)"))
                    conn.commit()
                    logger.info("✅ Созданы индексы для оптимизации производительности")
            except Exception as e:
                logger.warning(f"Предупреждение при создании индексов: {e}")
            
            logger.info("🎉 База данных готова к запуску проекта!")
            
        except Exception as e:
            logger.error(f"Ошибка при проверке готовности проекта: {e}")
            success = False
        
        return success

def main():
    """Основная функция"""
    # Получение URL базы данных из переменной окружения
    database_url = os.getenv("DATABASE_URL", "sqlite:///./triplan.db")
    
    # Устанавливаем DB_PATH для модуля database.py ПЕРЕД любыми импортами
    if database_url.startswith("sqlite:///"):
        db_path = database_url.replace("sqlite:///", "")
        os.environ["DB_PATH"] = db_path
        logger.info(f"Set DB_PATH environment variable to: {db_path}")
    
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
