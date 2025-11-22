#!/usr/bin/env python3
"""
Тест схем для проверки рекурсии
"""
import sys
import traceback

try:
    print("Importing schemas...")
    from schemas import CustomWorkoutCreate, WorkoutResponse
    from database import SportType, WorkoutType
    from datetime import date

    print("Creating test CustomWorkoutCreate...")
    test_create = CustomWorkoutCreate(
        uin="test123",
        date=date.today(),
        sport_type=SportType.RUNNING,
        duration_minutes=60,
        workout_type=WorkoutType.ENDURANCE
    )
    print(f"CustomWorkoutCreate created: {test_create}")

    print("\nCreating test WorkoutResponse...")
    test_response = WorkoutResponse(
        id=1,
        date=date.today(),
        sport_type=SportType.RUNNING,
        duration_minutes=60,
        workout_type=WorkoutType.ENDURANCE,
        is_completed=False,
        is_custom=True
    )
    print(f"WorkoutResponse created: {test_response}")

    print("\nTrying to repr WorkoutResponse...")
    print(repr(test_response))

    print("\n✓ All tests passed!")

except Exception as e:
    print(f"\n✗ Error occurred: {e}")
    traceback.print_exc()
    sys.exit(1)
