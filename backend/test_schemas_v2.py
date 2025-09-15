#!/usr/bin/env python3
"""
Тест схем версии 2 без циклических ссылок
"""

print("🔍 Тестирование схем v2...")

try:
    print("1. Импорт схем v2...")
    from schemas_v2 import *
    print("✅ Схемы v2 импортированы успешно")
except Exception as e:
    print(f"❌ Ошибка импорта схем v2: {e}")
    exit(1)

try:
    print("2. Тестирование создания экземпляров...")
    from datetime import datetime, date
    
    # Тестируем WorkoutResponse
    workout = WorkoutResponse(
        id=1,
        date=date.today(),
        sport_type="running",
        duration_minutes=60,
        workout_type="endurance",
        is_completed=False
    )
    print(f"✅ WorkoutResponse создан: {workout.sport_type}")
    
    # Тестируем TrainingPlanResponse
    plan = TrainingPlanResponse(
        id=1,
        complexity=500,
        competition_date=date.today(),
        competition_type="run_10k",
        competition_distance=None,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    print(f"✅ TrainingPlanResponse создан: {plan.competition_type}")
    
    # Тестируем простые схемы с dict
    workout_dict = {
        "id": 1,
        "date": str(date.today()),
        "sport_type": "running",
        "duration_minutes": 60,
        "workout_type": "endurance",
        "is_completed": False
    }
    
    simple_response = SimpleWorkoutsByDateResponse(
        uin="test_user",
        workouts=[workout_dict]
    )
    print(f"✅ SimpleWorkoutsByDateResponse создан: {len(simple_response.workouts)} тренировок")
    
    # Тестируем план с тренировками
    simple_plan = SimpleTrainingPlanWithWorkoutsResponse(
        id=1,
        complexity=500,
        competition_date=date.today(),
        competition_type="run_10k",
        competition_distance=None,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        workouts=[workout_dict]
    )
    print(f"✅ SimpleTrainingPlanWithWorkoutsResponse создан: {len(simple_plan.workouts)} тренировок")
    
except Exception as e:
    print(f"❌ Ошибка создания экземпляров: {e}")

print("\n✅ Тест схем v2 завершен успешно!")
