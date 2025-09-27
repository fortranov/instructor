"""
Схемы Pydantic без циклических ссылок (версия 2)
Используем forward references и отложенную инициализацию
"""

from __future__ import annotations
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, TYPE_CHECKING
from datetime import date, datetime
from database import SportType, WorkoutType, CompetitionType

# Схемы для создания плана
class TrainingPlanCreate(BaseModel):
    uin: str = Field(..., description="Уникальный идентификатор пользователя")
    complexity: int = Field(..., ge=0, le=1000, description="Сложность плана от 0 до 1000")
    competition_date: date = Field(..., description="Дата соревнования")
    competition_type: CompetitionType = Field(..., description="Тип соревнования")
    competition_distance: Optional[float] = Field(None, description="Дистанция для велосипеда (км) или плавания (м)")

# Схема тренировки (базовая, без ссылок)
class WorkoutResponse(BaseModel):
    id: int
    date: date
    sport_type: SportType
    duration_minutes: int
    workout_type: WorkoutType
    is_completed: bool = Field(default=False, description="Отмечена ли тренировка как выполненная")
    
    class Config:
        from_attributes = True

# Схема плана тренировок (базовая, без workouts)
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

# Схема для получения тренировок по датам
class WorkoutsByDateRequest(BaseModel):
    uin: str = Field(..., description="Уникальный идентификатор пользователя")
    start_date: date = Field(..., description="Начальная дата")
    end_date: date = Field(..., description="Конечная дата")

# Схемы для аутентификации
class UserRegistration(BaseModel):
    email: EmailStr = Field(..., description="Email пользователя")
    password: str = Field(..., min_length=6, description="Пароль (минимум 6 символов)")
    first_name: Optional[str] = Field(None, description="Имя")
    last_name: Optional[str] = Field(None, description="Фамилия")

class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="Email пользователя")
    password: str = Field(..., description="Пароль")

class UserResponse(BaseModel):
    id: int
    uin: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    is_active: bool
    preferred_workout_days: Optional[List[int]] = Field(default=[0,1,2,3,4,5,6], description="Предпочтительные дни для тренировок (0=понедельник, 6=воскресенье)")
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, description="Имя")
    last_name: Optional[str] = Field(None, description="Фамилия")
    email: Optional[EmailStr] = Field(None, description="Email")
    current_password: Optional[str] = Field(None, description="Текущий пароль")
    new_password: Optional[str] = Field(None, min_length=6, description="Новый пароль")
    preferred_workout_days: Optional[List[int]] = Field(None, description="Предпочтительные дни для тренировок (0=понедельник, 6=воскресенье)")

# Схема для обновления даты тренировки
class WorkoutDateUpdate(BaseModel):
    workout_id: int = Field(..., description="ID тренировки")
    new_date: date = Field(..., description="Новая дата тренировки")

# Схемы для мастера создания планов
class PlanWizardRequest(BaseModel):
    weekly_distance: str = Field(..., description="Недельный километраж")
    comfortable_pace: str = Field(..., description="Комфортный темп бега")
    target_distance: str = Field(..., description="Целевая дистанция")
    competition_date: date = Field(..., description="Дата соревнования")
    has_specific_goal: bool = Field(..., description="Есть ли конкретная цель")

class PlanWizardResponse(BaseModel):
    complexity: int = Field(..., description="Рассчитанная сложность плана")
    competition_type: CompetitionType = Field(..., description="Определенный тип соревнования")
    competition_date: date = Field(..., description="Дата соревнования")
    plan_id: int = Field(..., description="ID созданного плана")

# Простые схемы для ответов (без вложенных коллекций)
class SimpleWorkoutsByDateResponse(BaseModel):
    """Простой ответ с тренировками без вложенных объектов"""
    uin: str
    workouts: List[dict]  # Используем dict вместо WorkoutResponse
    
    class Config:
        from_attributes = True

class SimpleTrainingPlanWithWorkoutsResponse(BaseModel):
    """Простой план с тренировками без вложенных объектов"""
    id: int
    complexity: int
    competition_date: date
    competition_type: CompetitionType
    competition_distance: Optional[float]
    created_at: datetime
    updated_at: datetime
    workouts: List[dict]  # Используем dict вместо WorkoutResponse
    
    class Config:
        from_attributes = True

# Схемы для статистики
class WeeklyStats(BaseModel):
    """Статистика за неделю"""
    week_start: date
    week_end: date
    planned_duration: int  # Планируемая продолжительность в минутах
    completed_duration: int  # Выполненная продолжительность в минутах
    planned_workouts: int  # Количество запланированных тренировок
    completed_workouts: int  # Количество выполненных тренировок

class YearlyStatsResponse(BaseModel):
    """Статистика за год"""
    year: int
    total_planned_duration: int  # Общая запланированная продолжительность
    total_completed_duration: int  # Общая выполненная продолжительность
    total_planned_workouts: int  # Общее количество запланированных тренировок
    total_completed_workouts: int  # Общее количество выполненных тренировок
    weekly_stats: List[WeeklyStats]  # Статистика по неделям