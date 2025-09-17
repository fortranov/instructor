"""
API маршруты для сервиса планов тренировок
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import date, datetime

from database import get_db, User
from schemas import (
    TrainingPlanCreate, 
    TrainingPlanResponse, 
    SimpleTrainingPlanWithWorkoutsResponse,
    WorkoutsByDateRequest,
    UserRegistration,
    UserLogin,
    Token,
    UserResponse,
    UserUpdate,
    WorkoutDateUpdate
)
# Удалены импорты simple_schemas - endpoints перенесены в отдельные файлы
from plan_generator import PlanGenerator
from auth import (
    authenticate_user,
    create_user,
    create_access_token,
    get_current_active_user,
    get_password_hash,
    verify_password
)
import json

router = APIRouter()

def create_user_response(user: User) -> UserResponse:
    """Создать UserResponse из объекта User с правильной обработкой preferred_workout_days"""
    # Парсинг предпочтительных дней
    preferred_days = [0, 1, 2, 4, 5, 6]  # Значение по умолчанию
    if user.preferred_workout_days:
        try:
            preferred_days = json.loads(user.preferred_workout_days)
        except (json.JSONDecodeError, TypeError):
            preferred_days = [0, 1, 2, 4, 5, 6]  # Fallback к значению по умолчанию
    
    return UserResponse(
        id=user.id,
        uin=user.uin,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        is_active=bool(user.is_active),
        preferred_workout_days=preferred_days,
        created_at=user.created_at
    )

@router.post("/plans/create", status_code=status.HTTP_201_CREATED)
async def create_training_plan(
    plan_data: TrainingPlanCreate,
    db: Session = Depends(get_db)
):
    """
    Создать персонализированный план тренировок.
    
    Если у пользователя уже есть план, он будет заменен новым.
    """
    try:
        generator = PlanGenerator(db)
        plan = generator.create_training_plan(plan_data)
        return plan
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка создания плана: {str(e)}"
        )

@router.get("/plans/{uin}", response_model=TrainingPlanResponse)
async def get_training_plan(
    uin: str,
    db: Session = Depends(get_db)
):
    """
    Получить план тренировок пользователя по UIN.
    """
    generator = PlanGenerator(db)
    plan = generator.get_plan_by_uin(uin)
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"План тренировок для пользователя {uin} не найден"
        )
    
    return plan

# Endpoint перенесен в api_workouts.py

@router.delete("/plans/{uin}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_training_plan(
    uin: str,
    db: Session = Depends(get_db)
):
    """
    Удалить план тренировок пользователя.
    """
    generator = PlanGenerator(db)
    success = generator.delete_user_plan(uin)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"План тренировок для пользователя {uin} не найден"
        )

@router.put("/plans/{uin}/workouts/update-date", status_code=status.HTTP_200_OK)
async def update_workout_date(
    uin: str,
    workout_update: WorkoutDateUpdate,
    db: Session = Depends(get_db)
):
    """
    Обновить дату тренировки.
    """
    generator = PlanGenerator(db)
    success = generator.update_workout_date(
        uin=uin,
        workout_id=workout_update.workout_id,
        new_date=workout_update.new_date
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Тренировка с ID {workout_update.workout_id} не найдена или не принадлежит пользователю {uin}"
        )
    
    return {"message": "Дата тренировки успешно обновлена"}

@router.get("/health")
async def health_check():
    """
    Проверка работоспособности сервиса.
    """
    return {"status": "healthy", "message": "Triplan Backend Service is running"}

# Дополнительные эндпоинты для удобства

@router.get("/competition-types")
async def get_competition_types():
    """
    Получить список доступных типов соревнований.
    """
    from database import CompetitionType
    
    return {
        "running": [
            {"value": CompetitionType.RUN_10K.value, "label": "10 километров"},
            {"value": CompetitionType.RUN_HALF_MARATHON.value, "label": "Полумарафон"},
            {"value": CompetitionType.RUN_MARATHON.value, "label": "Марафон"}
        ],
        "cycling": [
            {"value": CompetitionType.CYCLING.value, "label": "Велосипед (указать дистанцию в км)"}
        ],
        "swimming": [
            {"value": CompetitionType.SWIMMING.value, "label": "Плавание (указать дистанцию в метрах)"}
        ],
        "triathlon": [
            {"value": CompetitionType.TRIATHLON_SPRINT.value, "label": "Спринт"},
            {"value": CompetitionType.TRIATHLON_OLYMPIC.value, "label": "Олимпийская дистанция"},
            {"value": CompetitionType.TRIATHLON_IRONMAN.value, "label": "Железная дистанция"}
        ]
    }

@router.get("/sport-types")
async def get_sport_types():
    """
    Получить список типов спорта.
    """
    from database import SportType
    
    return [
        {"value": SportType.RUNNING.value, "label": "Бег"},
        {"value": SportType.CYCLING.value, "label": "Велосипед"},
        {"value": SportType.SWIMMING.value, "label": "Плавание"}
    ]

@router.get("/workout-types")
async def get_workout_types():
    """
    Получить список типов тренировок.
    """
    from database import WorkoutType
    
    return [
        {"value": WorkoutType.ENDURANCE.value, "label": "Длительная"},
        {"value": WorkoutType.INTERVAL.value, "label": "Интервальная"},
        {"value": WorkoutType.RECOVERY.value, "label": "Восстанавливающая"}
    ]

# Маршруты аутентификации

@router.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserRegistration,
    db: Session = Depends(get_db)
):
    """
    Регистрация нового пользователя.
    """
    try:
        user = create_user(
            db=db,
            email=user_data.email,
            password=user_data.password,
            first_name=user_data.first_name,
            last_name=user_data.last_name
        )
        return create_user_response(user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка регистрации: {str(e)}"
        )

@router.post("/auth/login", response_model=Token)
async def login_user(
    user_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Вход пользователя в систему.
    """
    user = authenticate_user(db, user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email})
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=create_user_response(user)
    )

@router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(
    current_user = Depends(get_current_active_user)
):
    """
    Получить информацию о текущем пользователе.
    """
    return create_user_response(current_user)

@router.put("/auth/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Обновить информацию о текущем пользователе.
    """
    # Проверить текущий пароль если нужно изменить пароль или email
    if user_update.new_password or user_update.email:
        if not user_update.current_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Требуется текущий пароль для изменения email или пароля"
            )
        if not verify_password(user_update.current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверный текущий пароль"
            )
    
    # Обновить поля
    if user_update.first_name is not None:
        current_user.first_name = user_update.first_name
    if user_update.last_name is not None:
        current_user.last_name = user_update.last_name
    if user_update.email is not None:
        # Проверить, что email не занят
        existing_user = db.query(User).filter(User.email == user_update.email, User.id != current_user.id).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким email уже существует"
            )
        current_user.email = user_update.email
    if user_update.new_password:
        current_user.hashed_password = get_password_hash(user_update.new_password)
    if user_update.preferred_workout_days is not None:
        # Валидация дней недели
        if not all(0 <= day <= 6 for day in user_update.preferred_workout_days):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Дни недели должны быть от 0 (понедельник) до 6 (воскресенье)"
            )
        import json
        current_user.preferred_workout_days = json.dumps(user_update.preferred_workout_days)
    
    current_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)
    
    return create_user_response(current_user)

# Endpoints для отметок выполнения перенесены в api_completion.py
