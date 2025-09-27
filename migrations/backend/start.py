#!/usr/bin/env python3
"""
Скрипт для быстрого запуска Triplan Backend Service
"""

import subprocess
import sys
import os

def check_dependencies():
    """Проверить установленные зависимости"""
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import pydantic
        print("✅ Все зависимости установлены")
        return True
    except ImportError as e:
        print(f"❌ Отсутствует зависимость: {e}")
        print("Установите зависимости: pip install -r requirements.txt")
        return False

def start_server():
    """Запустить сервер"""
    if not check_dependencies():
        return
    
    print("🚀 Запуск Triplan Backend Service...")
    print("📝 Документация API: http://localhost:8000/docs")
    print("🏥 Health check: http://localhost:8000/api/v1/health")
    print("🔧 Для остановки нажмите Ctrl+C")
    print("-" * 50)
    
    try:
        # Запуск uvicorn сервера
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload",
            "--log-level", "info"
        ])
    except KeyboardInterrupt:
        print("\n👋 Сервер остановлен")
    except Exception as e:
        print(f"❌ Ошибка запуска сервера: {e}")

if __name__ == "__main__":
    start_server()
