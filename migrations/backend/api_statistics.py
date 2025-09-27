"""
API endpoints для статистики тренировок
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
from typing import List, Dict, Any
from calendar import monthrange

from database import get_db, User, Workout, WorkoutCompletionMark, TrainingPlan
from auth import get_current_active_user
from schemas import YearlyStatsResponse, WeeklyStats

# Создаем отдельный роутер для statistics endpoints
statistics_router = APIRouter()

def get_week_start(date_obj: date) -> date:
    """Получить начало недели (понедельник) для заданной даты"""
    days_since_monday = date_obj.weekday()
    return date_obj - timedelta(days=days_since_monday)

def get_week_end(date_obj: date) -> date:
    """Получить конец недели (воскресенье) для заданной даты"""
    return get_week_start(date_obj) + timedelta(days=6)

def get_weeks_in_year(year: int) -> List[Dict[str, date]]:
    """Получить все недели в году"""
    weeks = []
    
    # Начинаем с первого понедельника января
    jan_1 = date(year, 1, 1)
    week_start = get_week_start(jan_1)
    
    # Если 1 января не понедельник, начинаем с предыдущего понедельника
    if jan_1.weekday() != 0:
        week_start = jan_1 - timedelta(days=jan_1.weekday())
    
    current_date = week_start
    
    while current_date.year <= year:
        week_end = get_week_end(current_date)
        
        # Добавляем неделю только если она содержит дни из текущего года
        if week_end.year >= year or current_date.year == year:
            weeks.append({
                "start": current_date,
                "end": week_end
            })
        
        current_date += timedelta(days=7)
    
    return weeks

@statistics_router.get("/statistics/yearly/{year}", response_model=YearlyStatsResponse)
async def get_yearly_statistics(
    year: int,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> YearlyStatsResponse:
    """
    Получить статистику тренировок за год.
    """
    # Проверить, что год валидный
    if year < 2020 or year > 2030:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Год должен быть между 2020 и 2030"
        )
    
    # Получить план пользователя
    plan = db.query(TrainingPlan).filter(
        TrainingPlan.user_id == current_user.id
    ).first()
    
    if not plan:
        # Если плана нет, возвращаем пустую статистику
        return YearlyStatsResponse(
            year=year,
            total_planned_duration=0,
            total_completed_duration=0,
            total_planned_workouts=0,
            total_completed_workouts=0,
            weekly_stats=[]
        )
    
    # Получить все недели в году
    weeks = get_weeks_in_year(year)
    
    # Получить все тренировки пользователя за год
    year_start = date(year, 1, 1)
    year_end = date(year, 12, 31)
    
    workouts = db.query(Workout).filter(
        Workout.plan_id == plan.id,
        Workout.date >= year_start,
        Workout.date <= year_end
    ).all()
    
    # Отладочная информация
    print(f"Debug: Found {len(workouts)} workouts for plan {plan.id} in year {year}")
    
    # Создать словарь для быстрого поиска выполненных тренировок
    completed_workout_ids = set()
    completion_marks = db.query(WorkoutCompletionMark).filter(
        WorkoutCompletionMark.user_id == current_user.id,
        WorkoutCompletionMark.date >= year_start,
        WorkoutCompletionMark.date <= year_end
    ).all()
    
    print(f"Debug: Found {len(completion_marks)} completion marks for user {current_user.id}")
    
    for mark in completion_marks:
        completed_workout_ids.add(mark.workout_id)
    
    # Группировать тренировки по неделям
    weekly_stats = []
    total_planned_duration = 0
    total_completed_duration = 0
    total_planned_workouts = 0
    total_completed_workouts = 0
    
    for week in weeks:
        week_start = week["start"]
        week_end = week["end"]
        
        # Тренировки в этой неделе
        week_workouts = [
            w for w in workouts 
            if week_start <= w.date <= week_end
        ]
        
        planned_duration = sum(w.duration_minutes for w in week_workouts)
        planned_workouts = len(week_workouts)
        
        # Выполненные тренировки в этой неделе
        completed_workouts = [
            w for w in week_workouts 
            if w.id in completed_workout_ids
        ]
        
        completed_duration = sum(w.duration_minutes for w in completed_workouts)
        completed_workouts_count = len(completed_workouts)
        
        weekly_stats.append(WeeklyStats(
            week_start=week_start,
            week_end=week_end,
            planned_duration=planned_duration,
            completed_duration=completed_duration,
            planned_workouts=planned_workouts,
            completed_workouts=completed_workouts_count
        ))
        
        total_planned_duration += planned_duration
        total_completed_duration += completed_duration
        total_planned_workouts += planned_workouts
        total_completed_workouts += completed_workouts_count
    
    print(f"Debug: Final stats - planned: {total_planned_duration}, completed: {total_completed_duration}, weeks: {len(weekly_stats)}")
    
    return YearlyStatsResponse(
        year=year,
        total_planned_duration=total_planned_duration,
        total_completed_duration=total_completed_duration,
        total_planned_workouts=total_planned_workouts,
        total_completed_workouts=total_completed_workouts,
        weekly_stats=weekly_stats
    )

@statistics_router.get("/statistics/available-years")
async def get_available_years(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, List[int]]:
    """
    Получить список доступных годов для статистики.
    """
    # Получить план пользователя
    plan = db.query(TrainingPlan).filter(
        TrainingPlan.user_id == current_user.id
    ).first()
    
    if not plan:
        # Если плана нет, возвращаем текущий год
        current_year = datetime.now().year
        return {"years": [current_year]}
    
    # Получить все годы, в которых есть тренировки
    workouts = db.query(Workout).filter(
        Workout.plan_id == plan.id
    ).all()
    
    years = set()
    for workout in workouts:
        years.add(workout.date.year)
    
    # Если нет тренировок, добавляем текущий год
    if not years:
        current_year = datetime.now().year
        years.add(current_year)
    
    # Сортируем годы по возрастанию
    sorted_years = sorted(list(years))
    
    return {"years": sorted_years}
