#!/usr/bin/env python3
"""
Тест импорта енумов из database
"""

print("🔍 Тестирование импорта енумов...")

try:
    print("1. Импорт database модуля...")
    import database
    print("✅ database модуль импортирован")
except Exception as e:
    print(f"❌ Ошибка импорта database: {e}")
    exit(1)

try:
    print("2. Импорт отдельных енумов...")
    from database import SportType, WorkoutType, CompetitionType
    print("✅ Енумы импортированы успешно")
    
    # Тестируем использование
    print(f"   SportType.RUNNING = {SportType.RUNNING}")
    print(f"   WorkoutType.ENDURANCE = {WorkoutType.ENDURANCE}")
    print(f"   CompetitionType.RUN_10K = {CompetitionType.RUN_10K}")
    
except Exception as e:
    print(f"❌ Ошибка импорта енумов: {e}")
    exit(1)

try:
    print("3. Создание простой схемы с енумами...")
    from pydantic import BaseModel, Field
    from datetime import date
    
    class TestWorkout(BaseModel):
        sport_type: SportType
        workout_type: WorkoutType
        date: date
        
        class Config:
            from_attributes = True
    
    # Тестируем создание
    test_workout = TestWorkout(
        sport_type=SportType.RUNNING,
        workout_type=WorkoutType.ENDURANCE,
        date=date.today()
    )
    print(f"✅ Схема с енумами работает: {test_workout.sport_type}")
    
except Exception as e:
    print(f"❌ Ошибка схемы с енумами: {e}")

print("\n✅ Тест енумов завершен!")
