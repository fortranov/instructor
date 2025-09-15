#!/usr/bin/env python3
"""
Пошаговый тест схем для выявления циклических ссылок
"""

print("🔍 Пошаговое тестирование схем...")

try:
    print("1. Базовые импорты...")
    from pydantic import BaseModel, Field, EmailStr
    from typing import List, Optional
    from datetime import date, datetime
    from database import SportType, WorkoutType, CompetitionType
    print("✅ Базовые импорты успешны")
except Exception as e:
    print(f"❌ Ошибка базовых импортов: {e}")
    exit(1)

try:
    print("2. Создание TrainingPlanCreate...")
    class TrainingPlanCreate(BaseModel):
        uin: str = Field(..., description="Уникальный идентификатор пользователя")
        complexity: int = Field(..., ge=0, le=1000, description="Сложность плана от 0 до 1000")
        competition_date: date = Field(..., description="Дата соревнования")
        competition_type: CompetitionType = Field(..., description="Тип соревнования")
        competition_distance: Optional[float] = Field(None, description="Дистанция для велосипеда (км) или плавания (м)")
    print("✅ TrainingPlanCreate создан")
except Exception as e:
    print(f"❌ Ошибка TrainingPlanCreate: {e}")
    exit(1)

try:
    print("3. Создание WorkoutResponse...")
    class WorkoutResponse(BaseModel):
        id: int
        date: date
        sport_type: SportType
        duration_minutes: int
        workout_type: WorkoutType
        is_completed: bool = Field(default=False, description="Отмечена ли тренировка как выполненная")
        
        class Config:
            from_attributes = True
    print("✅ WorkoutResponse создан")
except Exception as e:
    print(f"❌ Ошибка WorkoutResponse: {e}")
    exit(1)

try:
    print("4. Создание TrainingPlanResponse (без workouts)...")
    class TrainingPlanResponse(BaseModel):
        id: int
        complexity: int
        competition_date: date
        competition_type: CompetitionType
        competition_distance: Optional[float]
        created_at: datetime
        updated_at: datetime
        
        class Config:
            from_attributes = True
    print("✅ TrainingPlanResponse создан")
except Exception as e:
    print(f"❌ Ошибка TrainingPlanResponse: {e}")
    exit(1)

try:
    print("5. Создание TrainingPlanWithWorkoutsResponse (с workouts)...")
    class TrainingPlanWithWorkoutsResponse(BaseModel):
        id: int
        complexity: int
        competition_date: date
        competition_type: CompetitionType
        competition_distance: Optional[float]
        created_at: datetime
        updated_at: datetime
        workouts: List[WorkoutResponse]  # ЭТО МОЖЕТ БЫТЬ ПРОБЛЕМОЙ!
        
        class Config:
            from_attributes = True
    print("❌ TrainingPlanWithWorkoutsResponse создан - НЕ ДОЛЖНО БЫТЬ!")
except Exception as e:
    print(f"✅ Ошибка TrainingPlanWithWorkoutsResponse (ожидаемо): циклическая ссылка обнаружена")

print("\n🎯 Пошаговый тест завершен!")
