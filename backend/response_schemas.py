"""
Простые схемы для ответов API без циклических зависимостей
"""

from pydantic import BaseModel
from typing import List
from datetime import date, datetime
from database import SportType, WorkoutType, CompetitionType

# Простая схема тренировки для ответов
class WorkoutResponseSimple(BaseModel):
    id: int
    date: date
    sport_type: SportType
    duration_minutes: int
    workout_type: WorkoutType
    is_completed: bool = False
    
    class Config:
        from_attributes = True

# Схема ответа с тренировками по датам
class WorkoutsByDateResponseSimple(BaseModel):
    uin: str
    workouts: List[WorkoutResponseSimple]

# Схема отметки выполнения тренировки
class WorkoutCompletionMarkResponseSimple(BaseModel):
    id: int
    workout_id: int
    user_id: int
    date: date
    completed_at: datetime
    
    class Config:
        from_attributes = True

# Схема для создания отметки выполнения
class WorkoutCompletionMarkCreateSimple(BaseModel):
    workout_id: int
    date: date
