#!/usr/bin/env python3
"""
Скрипт для выполнения миграций базы данных в продакшене
"""

import os
import sys
import argparse
from migrations.migration_manager import MigrationManager

def main():
    """Главная функция для запуска миграций"""
    parser = argparse.ArgumentParser(description="Управление миграциями базы данных TriPlan")
    parser.add_argument("command", choices=["migrate", "rollback", "status"], 
                       help="Команда для выполнения")
    parser.add_argument("--version", "-v", help="Версия для миграции или отката")
    parser.add_argument("--db-path", help="Путь к файлу базы данных")
    
    args = parser.parse_args()
    
    # Настроить путь к базе данных
    db_path = args.db_path or os.getenv("DB_PATH", "../triplan.db")
    
    # Создать менеджер миграций
    manager = MigrationManager(db_path)
    
    print(f"🗄️  База данных: {os.path.abspath(db_path)}")
    print(f"📅 Время: {os.popen('date /t && time /t').read().strip()}")
    print()
    
    if args.command == "migrate":
        print("🚀 Выполнение миграций...")
        success = manager.run_migrations(args.version)
        sys.exit(0 if success else 1)
        
    elif args.command == "rollback":
        if not args.version:
            print("❌ Ошибка: Для отката необходимо указать версию")
            print("Использование: python run_migrations.py rollback --version 001")
            sys.exit(1)
        
        print(f"⏪ Откат до версии {args.version}...")
        success = manager.rollback_to_version(args.version)
        sys.exit(0 if success else 1)
        
    elif args.command == "status":
        manager.status()
        sys.exit(0)

if __name__ == "__main__":
    main()
