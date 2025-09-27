"""
API endpoints для тренировок
Изолированные от основных схем для избежания циклических зависимостей
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from datetime import date

from database import get_db, User, Workout, WorkoutCompletionMark
from plan_generator import PlanGenerator
from schemas import SimpleWorkoutsByDateResponse

# Создаем отдельный роутер для workout endpoints
workouts_router = APIRouter()

@workouts_router.get("/plans/{uin}/workouts")
async def get_workouts_by_date_range(
    uin: str,
    start_date: date = Query(..., description="Начальная дата (YYYY-MM-DD)"),
    end_date: date = Query(..., description="Конечная дата (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Получить тренировки пользователя в указанном диапазоне дат.
    """
    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Начальная дата не может быть позже конечной даты"
        )
    
    generator = PlanGenerator(db)
    workout_dicts = generator.get_workouts_by_date_range(uin, start_date, end_date)
    
    # Преобразовать словари в простые объекты
    workouts = []
    for workout_dict in workout_dicts:
        workouts.append({
            "id": workout_dict['id'],
            "date": str(workout_dict['date']),
            "sport_type": workout_dict['sport_type'].value,
            "duration_minutes": workout_dict['duration_minutes'],
            "workout_type": workout_dict['workout_type'].value,
            "is_completed": workout_dict['is_completed']
        })
    
    return {
        "uin": uin,
        "workouts": workouts
    }
