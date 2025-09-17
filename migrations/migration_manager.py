#!/usr/bin/env python3
"""
Менеджер миграций базы данных для TriPlan
"""

import sqlite3
import os
import json
import importlib
from typing import List, Dict, Any
from datetime import datetime

class MigrationManager:
    """Класс для управления миграциями базы данных"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or os.getenv("DB_PATH", "./triplan.db")
        self.migrations_table = "schema_migrations"
    
    def get_connection(self) -> sqlite3.Connection:
        """Получить подключение к базе данных"""
        return sqlite3.connect(self.db_path)
    
    def create_migrations_table(self):
        """Создать таблицу для отслеживания миграций"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.migrations_table} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version VARCHAR(255) NOT NULL UNIQUE,
                description TEXT NOT NULL,
                executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                checksum VARCHAR(255)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def get_executed_migrations(self) -> List[str]:
        """Получить список выполненных миграций"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(f"SELECT version FROM {self.migrations_table} ORDER BY version")
            return [row[0] for row in cursor.fetchall()]
        except sqlite3.OperationalError:
            # Таблица миграций не существует
            return []
        finally:
            conn.close()
    
    def mark_migration_executed(self, version: str, description: str, checksum: str = None):
        """Отметить миграцию как выполненную"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(f"""
            INSERT INTO {self.migrations_table} (version, description, checksum)
            VALUES (?, ?, ?)
        """, (version, description, checksum))
        
        conn.commit()
        conn.close()
    
    def execute_migration(self, migration_module):
        """Выполнить миграцию"""
        try:
            # Выполнить миграцию
            migration_module.up()
            
            # Отметить как выполненную
            self.mark_migration_executed(
                migration_module.version,
                migration_module.description,
                getattr(migration_module, 'checksum', None)
            )
            
            print(f"✅ Миграция {migration_module.version} выполнена успешно")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка при выполнении миграции {migration_module.version}: {e}")
            return False
    
    def rollback_migration(self, migration_module):
        """Откатить миграцию"""
        try:
            # Выполнить откат
            migration_module.down()
            
            # Удалить запись о миграции
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(f"DELETE FROM {self.migrations_table} WHERE version = ?", 
                          (migration_module.version,))
            
            conn.commit()
            conn.close()
            
            print(f"✅ Миграция {migration_module.version} откачена успешно")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка при откате миграции {migration_module.version}: {e}")
            return False
    
    def get_pending_migrations(self) -> List[str]:
        """Получить список миграций, которые нужно выполнить"""
        executed = self.get_executed_migrations()
        all_migrations = self.get_all_migrations()
        
        return [migration for migration in all_migrations if migration not in executed]
    
    def get_all_migrations(self) -> List[str]:
        """Получить список всех доступных миграций"""
        migrations_dir = os.path.dirname(__file__)
        migrations = []
        
        for filename in os.listdir(migrations_dir):
            if (filename.startswith("migration_") and 
                filename.endswith(".py") and 
                filename != "migration_manager.py"):
                version = filename.replace("migration_", "").replace(".py", "")
                migrations.append(version)
        
        return sorted(migrations)
    
    def run_migrations(self, target_version: str = None):
        """Выполнить все ожидающие миграции"""
        print("🔄 Запуск миграций базы данных...")
        
        # Создать таблицу миграций если её нет
        self.create_migrations_table()
        
        # Получить список миграций для выполнения
        pending_migrations = self.get_pending_migrations()
        
        if target_version:
            pending_migrations = [m for m in pending_migrations if m <= target_version]
        
        if not pending_migrations:
            print("✅ Все миграции уже выполнены")
            return True
        
        print(f"📋 Найдено {len(pending_migrations)} миграций для выполнения:")
        for migration in pending_migrations:
            print(f"  - {migration}")
        
        # Выполнить миграции
        success = True
        for migration_version in pending_migrations:
            try:
                migration_module = importlib.import_module(f"migrations.migration_{migration_version}")
                if not self.execute_migration(migration_module):
                    success = False
                    break
            except ImportError as e:
                print(f"❌ Не удалось загрузить миграцию {migration_version}: {e}")
                success = False
                break
        
        if success:
            print("✅ Все миграции выполнены успешно!")
        else:
            print("❌ Некоторые миграции завершились с ошибками")
        
        return success
    
    def rollback_to_version(self, target_version: str):
        """Откатить миграции до указанной версии"""
        print(f"🔄 Откат миграций до версии {target_version}...")
        
        executed = self.get_executed_migrations()
        migrations_to_rollback = [m for m in executed if m > target_version]
        
        if not migrations_to_rollback:
            print("✅ Нет миграций для отката")
            return True
        
        print(f"📋 Найдено {len(migrations_to_rollback)} миграций для отката:")
        for migration in reversed(migrations_to_rollback):
            print(f"  - {migration}")
        
        # Откатить миграции в обратном порядке
        success = True
        for migration_version in reversed(migrations_to_rollback):
            try:
                migration_module = importlib.import_module(f"migrations.migration_{migration_version}")
                if not self.rollback_migration(migration_module):
                    success = False
                    break
            except ImportError as e:
                print(f"❌ Не удалось загрузить миграцию {migration_version}: {e}")
                success = False
                break
        
        if success:
            print("✅ Откат миграций выполнен успешно!")
        else:
            print("❌ Некоторые миграции не удалось откатить")
        
        return success
    
    def status(self):
        """Показать статус миграций"""
        print("📊 Статус миграций:")
        
        executed = self.get_executed_migrations()
        all_migrations = self.get_all_migrations()
        pending = self.get_pending_migrations()
        
        print(f"  Всего миграций: {len(all_migrations)}")
        print(f"  Выполнено: {len(executed)}")
        print(f"  Ожидает выполнения: {len(pending)}")
        
        if executed:
            print("\n✅ Выполненные миграции:")
            for migration in executed:
                print(f"  - {migration}")
        
        if pending:
            print("\n⏳ Ожидающие миграции:")
            for migration in pending:
                print(f"  - {migration}")


def main():
    """Главная функция для запуска миграций из командной строки"""
    import sys
    
    manager = MigrationManager()
    
    if len(sys.argv) < 2:
        print("Использование:")
        print("  python migration_manager.py migrate [version]  - Выполнить миграции")
        print("  python migration_manager.py rollback <version> - Откатить до версии")
        print("  python migration_manager.py status            - Показать статус")
        return
    
    command = sys.argv[1]
    
    if command == "migrate":
        target_version = sys.argv[2] if len(sys.argv) > 2 else None
        manager.run_migrations(target_version)
    elif command == "rollback":
        if len(sys.argv) < 3:
            print("❌ Укажите версию для отката")
            return
        target_version = sys.argv[2]
        manager.rollback_to_version(target_version)
    elif command == "status":
        manager.status()
    else:
        print(f"❌ Неизвестная команда: {command}")


if __name__ == "__main__":
    main()
