#!/usr/bin/env python3
"""
Тест импортов для выявления циклических ссылок Pydantic
"""

print("🔍 Тестирование импортов на циклические ссылки...")

try:
    print("1. Импорт database...")
    from database import *
    print("✅ database импортирован успешно")
except Exception as e:
    print(f"❌ Ошибка импорта database: {e}")
    exit(1)

try:
    print("2. Импорт простых схем completion...")
    from simple_completion_schemas import *
    print("✅ simple_completion_schemas импортированы успешно")
except Exception as e:
    print(f"❌ Ошибка импорта simple_completion_schemas: {e}")

try:
    print("3. Импорт основных схем...")
    from schemas import *
    print("❌ schemas импортированы - есть циклические ссылки!")
except Exception as e:
    print(f"❌ Ошибка импорта schemas (ожидаемо): циклические ссылки найдены")

try:
    print("4. Тестирование отдельных схем...")
    from schemas import TrainingPlanCreate, UserRegistration, UserLogin, Token, UserResponse, UserUpdate, WorkoutDateUpdate
    print("✅ Базовые схемы без циклических ссылок импортированы")
except Exception as e:
    print(f"❌ Ошибка импорта базовых схем: {e}")

try:
    print("5. Тестирование проблемных схем...")
    from schemas import WorkoutResponse
    print("⚠️ WorkoutResponse импортирован - проверяем...")
except Exception as e:
    print(f"❌ Ошибка импорта WorkoutResponse: {e}")

try:
    print("6. Тестирование схем планов...")
    from schemas import TrainingPlanResponse
    print("⚠️ TrainingPlanResponse импортирован - проверяем...")
except Exception as e:
    print(f"❌ Ошибка импорта TrainingPlanResponse: {e}")

print("\n🎯 Анализ завершен!")
