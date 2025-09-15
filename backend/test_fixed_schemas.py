#!/usr/bin/env python3
"""
Тест исправленных схем без циклических ссылок
"""

print("🔍 Тестирование исправленных схем...")

try:
    print("1. Импорт исправленных схем...")
    from schemas_fixed import *
    print("✅ Базовые схемы импортированы успешно")
except Exception as e:
    print(f"❌ Ошибка импорта базовых схем: {e}")
    exit(1)

try:
    print("2. Создание схем с коллекциями...")
    TrainingPlanWithWorkoutsResponse = create_training_plan_with_workouts_response()
    WorkoutsByDateResponse = create_workouts_by_date_response()
    print("✅ Схемы с коллекциями созданы динамически")
except Exception as e:
    print(f"❌ Ошибка создания схем с коллекциями: {e}")
    exit(1)

try:
    print("3. Тестирование создания экземпляров...")
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
    
    # Тестируем схему с коллекциями
    workouts_response = WorkoutsByDateResponse(
        uin="test_user",
        workouts=[workout]
    )
    print(f"✅ WorkoutsByDateResponse создан: {len(workouts_response.workouts)} тренировок")
    
except Exception as e:
    print(f"❌ Ошибка создания экземпляров: {e}")

print("\n✅ Тест исправленных схем завершен!")
