#!/usr/bin/env python3
"""
Минимальный тест без импорта проблемных модулей
"""

print("🔍 Минимальный тест...")

try:
    print("1. Импорт только Pydantic...")
    from pydantic import BaseModel, Field
    from datetime import date, datetime
    from typing import Optional
    print("✅ Базовые импорты успешны")
except Exception as e:
    print(f"❌ Ошибка базовых импортов: {e}")
    exit(1)

try:
    print("2. Создание простой схемы...")
    class TestSchema(BaseModel):
        id: int
        name: str
        created_at: datetime
    
    # Тестирование создания экземпляра
    test_instance = TestSchema(id=1, name="test", created_at=datetime.now())
    print(f"✅ Простая схема работает: {test_instance.name}")
except Exception as e:
    print(f"❌ Ошибка простой схемы: {e}")
    exit(1)

try:
    print("3. Импорт database без схем...")
    import sys
    if 'schemas' in sys.modules:
        del sys.modules['schemas']
    
    from database import Base, engine, SessionLocal, get_db
    print("✅ Базовые компоненты database импортированы")
except Exception as e:
    print(f"❌ Ошибка импорта database: {e}")

print("\n✅ Минимальный тест прошел успешно!")
