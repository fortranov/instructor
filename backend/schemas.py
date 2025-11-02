"""
Схемы Pydantic без циклических ссылок (версия 2)
Используем forward references и отложенную инициализацию
"""

from __future__ import annotations
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, TYPE_CHECKING
from datetime import date, datetime
from database import SportType, WorkoutType, CompetitionType, TariffType

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
    sport_type: Optional[str] = Field(None, description="Вид спорта (running, cycling, swimming, triathlon)")
    weekly_distance: str = Field(..., description="Недельный километраж")
    comfortable_pace: str = Field(..., description="Комфортный темп бега")
    target_distance: str = Field(..., description="Целевая дистанция")
    competition_date: date = Field(..., description="Дата соревнования")
    has_specific_goal: bool = Field(..., description="Есть ли конкретная цель")
    has_strength_training: bool = Field(default=False, description="Есть ли возможность заниматься силовыми тренировками")
    preferred_workout_days: List[int] = Field(default=[0,1,2,3,4,5,6], description="Предпочтительные дни для тренировок (0=понедельник, 6=воскресенье)")

class PlanWizardResponse(BaseModel):
    complexity: int = Field(..., description="Рассчитанная сложность плана")
    competition_type: CompetitionType = Field(..., description="Определенный тип соревнования")
    competition_date: date = Field(..., description="Дата соревнования")
    plan_id: int = Field(..., description="ID созданного плана")

class WeeklyWorkoutCountRequest(BaseModel):
    sport_type: Optional[str] = Field(None, description="Вид спорта (running, cycling, swimming, triathlon)")
    weekly_distance: str = Field(..., description="Недельный километраж")
    comfortable_pace: str = Field(..., description="Комфортный темп бега")
    target_distance: str = Field(..., description="Целевая дистанция")
    competition_date: date = Field(..., description="Дата соревнования")
    has_specific_goal: bool = Field(..., description="Есть ли конкретная цель")

class WeeklyWorkoutCountResponse(BaseModel):
    max_weekly_workouts: int = Field(..., description="Максимальное количество тренировок в неделю")
    complexity: int = Field(..., description="Рассчитанная сложность плана")
    competition_type: CompetitionType = Field(..., description="Определенный тип соревнования")

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

# Схемы для настроек приложения
class AppSettingResponse(BaseModel):
    """Настройка приложения"""
    id: int
    key: str
    value: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class AppSettingUpdate(BaseModel):
    """Обновление настройки приложения"""
    key: str
    value: str
    description: Optional[str] = None

# Схемы для тарифного плана пользователя
class UserTariffResponse(BaseModel):
    """Информация о тарифе пользователя"""
    tariff_type: Optional[str] = None
    tariff_name: Optional[str] = None
    test_period_days_remaining: Optional[int] = None  # Количество дней до конца тестового периода
    test_period_end_date: Optional[str] = None  # Дата окончания тестового периода
    
    class Config:
        from_attributes = True

class TariffPurchaseRequest(BaseModel):
    """Запрос на покупку/продление тарифа"""
    tariff_type: str = Field(..., description="Тип тарифа")
    months: int = Field(..., ge=1, le=12, description="Количество месяцев")
    
class TariffPriceResponse(BaseModel):
    """Информация о цене тарифа"""
    base_price: float
    months: int
    discount_percent: int
    final_price: float
    total_savings: float

# Схемы для администрирования

# Схемы для тарифов
class TariffResponse(BaseModel):
    """Ответ с информацией о тарифе"""
    id: int
    name: str
    type: TariffType
    view_full_plan: bool
    view_two_weeks: bool
    allow_running: bool = Field(default=True, description="Доступен ли бег")
    allow_cycling: bool = Field(default=False, description="Доступен ли велосипед")
    allow_swimming: bool = Field(default=False, description="Доступно ли плавание")
    allow_triathlon: bool = Field(default=False, description="Доступен ли триатлон")
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class TariffUpdate(BaseModel):
    """Обновление настроек тарифа"""
    view_full_plan: bool = Field(..., description="Просмотр всего плана")
    view_two_weeks: bool = Field(..., description="Просмотр двух недель")
    allow_running: bool = Field(default=True, description="Доступен ли бег")
    allow_cycling: bool = Field(default=False, description="Доступен ли велосипед")
    allow_swimming: bool = Field(default=False, description="Доступно ли плавание")
    allow_triathlon: bool = Field(default=False, description="Доступен ли триатлон")

class TariffsUpdateRequest(BaseModel):
    """Запрос на обновление всех тарифов"""
    test: TariffUpdate
    trial: TariffUpdate
    pro: TariffUpdate

# Схемы для пользователей (администрирование)
class AdminUserResponse(BaseModel):
    """Ответ с информацией о пользователе для администратора"""
    id: int
    uin: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    is_active: bool
    tariff_type: Optional[TariffType]
    tariff_name: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserTariffUpdate(BaseModel):
    """Обновление тарифа пользователя"""
    user_id: int = Field(..., description="ID пользователя")
    tariff_type: TariffType = Field(..., description="Новый тариф")

# Схемы для коэффициентов тренировок
class WorkoutCoefficientsResponse(BaseModel):
    """Ответ с коэффициентами тренировок"""
    id: int
    # Коэффициенты для недельного километража
    weekly_distance_beginner: int
    weekly_distance_5_10: int
    weekly_distance_10_30: int
    weekly_distance_30_50: int
    weekly_distance_50_plus: int
    
    # Коэффициенты для комфортного темпа
    pace_8_plus: int
    pace_7_8: int
    pace_6_7: int
    pace_5_6: int
    pace_4_5: int
    pace_4_minus: int
    
    # Коэффициенты для целевой дистанции
    target_distance_5k: int
    target_distance_10k: int
    target_distance_21k: int
    target_distance_42k: int
    
    # Коэффициенты для времени подготовки
    time_preparation_base: int
    time_preparation_weeks_optimal: int
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class WorkoutCoefficientsUpdate(BaseModel):
    """Обновление коэффициентов тренировок"""
    # Коэффициенты для недельного километража
    weekly_distance_beginner: int = Field(..., ge=0, le=1000)
    weekly_distance_5_10: int = Field(..., ge=0, le=1000)
    weekly_distance_10_30: int = Field(..., ge=0, le=1000)
    weekly_distance_30_50: int = Field(..., ge=0, le=1000)
    weekly_distance_50_plus: int = Field(..., ge=0, le=1000)
    
    # Коэффициенты для комфортного темпа
    pace_8_plus: int = Field(..., ge=0, le=1000)
    pace_7_8: int = Field(..., ge=0, le=1000)
    pace_6_7: int = Field(..., ge=0, le=1000)
    pace_5_6: int = Field(..., ge=0, le=1000)
    pace_4_5: int = Field(..., ge=0, le=1000)
    pace_4_minus: int = Field(..., ge=0, le=1000)
    
    # Коэффициенты для целевой дистанции
    target_distance_5k: int = Field(..., ge=0, le=1000)
    target_distance_10k: int = Field(..., ge=0, le=1000)
    target_distance_21k: int = Field(..., ge=0, le=1000)
    target_distance_42k: int = Field(..., ge=0, le=1000)
    
    # Коэффициенты для времени подготовки
    time_preparation_base: int = Field(..., ge=0, le=1000)
    time_preparation_weeks_optimal: int = Field(..., ge=1, le=52)