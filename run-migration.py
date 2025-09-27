#!/usr/bin/env python3
"""
Простой скрипт для запуска миграций без Docker
"""

import os
import sys
import subprocess

def main():
    """Запуск миграций"""
    print("🚀 Запуск миграций базы данных...")
    
    # Переходим в папку migrations
    migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')
    if not os.path.exists(migrations_dir):
        print("❌ Папка migrations не найдена")
        sys.exit(1)
    
    # Запускаем миграции
    try:
        result = subprocess.run([
            sys.executable, 'migration_runner.py'
        ], cwd=migrations_dir, check=True, capture_output=True, text=True)
        
        print("✅ Миграции выполнены успешно!")
        print(result.stdout)
        
    except subprocess.CalledProcessError as e:
        print("❌ Ошибка при выполнении миграций:")
        print(e.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

