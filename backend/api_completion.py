"""
API endpoints для отметок выполнения тренировок
Изолированные от основных схем для избежания циклических зависимостей
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date, datetime
from typing import Dict, Any

from database import get_db, User, Workout, WorkoutCompletionMark
from auth import get_current_active_user

# Создаем отдельный роутер для completion endpoints
completion_router = APIRouter()

@completion_router.post("/workouts/{workout_id}/completion", status_code=status.HTTP_201_CREATED)
async def mark_workout_completed(
    workout_id: int,
    completion_data: Dict[str, Any],  # Используем простой dict вместо Pydantic
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Отметить тренировку как выполненную.
    """
    # Проверить, что тренировка существует и принадлежит пользователю
    workout = db.query(Workout).join(Workout.plan).filter(
        Workout.id == workout_id,
        Workout.plan.has(user_id=current_user.id)
    ).first()
    
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тренировка не найдена или не принадлежит пользователю"
        )
    
    # Проверить, что тренировка еще не отмечена как выполненная
    existing_mark = db.query(WorkoutCompletionMark).filter(
        WorkoutCompletionMark.workout_id == workout_id,
        WorkoutCompletionMark.user_id == current_user.id
    ).first()
    
    if existing_mark:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Тренировка уже отмечена как выполненная"
        )
    
    # Создать отметку выполнения
    completion_mark = WorkoutCompletionMark(
        workout_id=workout_id,
        user_id=current_user.id,
        date=date.fromisoformat(completion_data.get("date", str(date.today())))
    )
    
    db.add(completion_mark)
    db.commit()
    db.refresh(completion_mark)
    
    return {
        "id": completion_mark.id,
        "workout_id": completion_mark.workout_id,
        "user_id": completion_mark.user_id,
        "date": str(completion_mark.date),
        "completed_at": completion_mark.completed_at.isoformat()
    }

@completion_router.delete("/workouts/{workout_id}/completion", status_code=status.HTTP_204_NO_CONTENT)
async def unmark_workout_completed(
    workout_id: int,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Убрать отметку о выполнении тренировки.
    """
    # Проверить, что тренировка существует и принадлежит пользователю
    workout = db.query(Workout).join(Workout.plan).filter(
        Workout.id == workout_id,
        Workout.plan.has(user_id=current_user.id)
    ).first()
    
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тренировка не найдена или не принадлежит пользователю"
        )
    
    # Найти и удалить отметку выполнения
    completion_mark = db.query(WorkoutCompletionMark).filter(
        WorkoutCompletionMark.workout_id == workout_id,
        WorkoutCompletionMark.user_id == current_user.id
    ).first()
    
    if not completion_mark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Отметка о выполнении тренировки не найдена"
        )
    
    db.delete(completion_mark)
    db.commit()

@completion_router.get("/workouts/{workout_id}/completion")
async def get_workout_completion(
    workout_id: int,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Получить информацию об отметке выполнения тренировки.
    """
    # Проверить, что тренировка существует и принадлежит пользователю
    workout = db.query(Workout).join(Workout.plan).filter(
        Workout.id == workout_id,
        Workout.plan.has(user_id=current_user.id)
    ).first()
    
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тренировка не найдена или не принадлежит пользователю"
        )
    
    # Найти отметку выполнения
    completion_mark = db.query(WorkoutCompletionMark).filter(
        WorkoutCompletionMark.workout_id == workout_id,
        WorkoutCompletionMark.user_id == current_user.id
    ).first()
    
    if not completion_mark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Отметка о выполнении тренировки не найдена"
        )
    
    return {
        "id": completion_mark.id,
        "workout_id": completion_mark.workout_id,
        "user_id": completion_mark.user_id,
        "date": str(completion_mark.date),
        "completed_at": completion_mark.completed_at.isoformat()
    }
