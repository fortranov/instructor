#!/usr/bin/env python3
"""
Тест импорта всех модулей backend
"""

print("🔍 Тестирование импорта всех модулей...")

try:
    print("1. Импорт database...")
    import database
    print("✅ database импортирован")
except Exception as e:
    print(f"❌ Ошибка database: {e}")
    exit(1)

try:
    print("2. Импорт schemas...")
    import schemas
    print("✅ schemas импортирован")
except Exception as e:
    print(f"❌ Ошибка schemas: {e}")
    exit(1)

try:
    print("3. Импорт simple_completion_schemas...")
    import simple_completion_schemas
    print("✅ simple_completion_schemas импортирован")
except Exception as e:
    print(f"❌ Ошибка simple_completion_schemas: {e}")

try:
    print("4. Импорт auth...")
    import auth
    print("✅ auth импортирован")
except Exception as e:
    print(f"❌ Ошибка auth: {e}")

try:
    print("5. Импорт plan_generator...")
    import plan_generator
    print("✅ plan_generator импортирован")
except Exception as e:
    print(f"❌ Ошибка plan_generator: {e}")

try:
    print("6. Импорт api_completion...")
    import api_completion
    print("✅ api_completion импортирован")
except Exception as e:
    print(f"❌ Ошибка api_completion: {e}")

try:
    print("7. Импорт api_workouts...")
    import api_workouts
    print("✅ api_workouts импортирован")
except Exception as e:
    print(f"❌ Ошибка api_workouts: {e}")

try:
    print("8. Импорт api_routes...")
    import api_routes
    print("✅ api_routes импортирован")
except Exception as e:
    print(f"❌ Ошибка api_routes: {e}")

try:
    print("9. Импорт main...")
    import main
    print("✅ main импортирован")
except Exception as e:
    print(f"❌ Ошибка main: {e}")

print("\n🎉 Все модули импортированы успешно!")
