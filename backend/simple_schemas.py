"""
Простые схемы без циклических зависимостей для API
"""

from pydantic import BaseModel
from typing import List
from datetime import date, datetime

# Простые схемы тренировок
class SimpleWorkout(BaseModel):
    id: int
    date: date
    sport_type: str
    duration_minutes: int
    workout_type: str
    is_completed: bool = False

class SimpleWorkoutsList(BaseModel):
    uin: str
    workouts: List[SimpleWorkout]

# Простые схемы для отметок выполнения
class SimpleCompletionMark(BaseModel):
    id: int
    workout_id: int
    user_id: int
    date: date
    completed_at: datetime

class SimpleCompletionCreate(BaseModel):
    workout_id: int
    date: date
