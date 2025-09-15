from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import date, datetime
from database import SportType, WorkoutType, CompetitionType

# Схемы для создания плана
class TrainingPlanCreate(BaseModel):
    uin: str = Field(..., description="Уникальный идентификатор пользователя")
    complexity: int = Field(..., ge=0, le=1000, description="Сложность плана от 0 до 1000")
    competition_date: date = Field(..., description="Дата соревнования")
    competition_type: CompetitionType = Field(..., description="Тип соревнования")
    competition_distance: Optional[float] = Field(None, description="Дистанция для велосипеда (км) или плавания (м)")

# Схема тренировки
class WorkoutResponse(BaseModel):
    id: int
    date: date
    sport_type: SportType
    duration_minutes: int
    workout_type: WorkoutType
    is_completed: bool = Field(default=False, description="Отмечена ли тренировка как выполненная")
    
    class Config:
        from_attributes = True

# Схема плана тренировок (без workouts для избежания циклических ссылок)
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

# Схема для обновления даты тренировки
class WorkoutDateUpdate(BaseModel):
    workout_id: int = Field(..., description="ID тренировки")
    new_date: date = Field(..., description="Новая дата тренировки")

# Схемы с коллекциями создаем отдельно, чтобы избежать циклических ссылок
# Эти схемы создаются динамически в runtime, когда нужны

def create_training_plan_with_workouts_response():
    """Создает схему плана с тренировками динамически"""
    class TrainingPlanWithWorkoutsResponse(BaseModel):
        id: int
        complexity: int
        competition_date: date
        competition_type: CompetitionType
        competition_distance: Optional[float]
        created_at: datetime
        updated_at: datetime
        workouts: List[WorkoutResponse]
        
        class Config:
            from_attributes = True
    
    return TrainingPlanWithWorkoutsResponse

def create_workouts_by_date_response():
    """Создает схему ответа с тренировками по датам динамически"""
    class WorkoutsByDateResponse(BaseModel):
        uin: str
        workouts: List[WorkoutResponse]
        
        class Config:
            from_attributes = True
    
    return WorkoutsByDateResponse
