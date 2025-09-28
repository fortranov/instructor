"""
API endpoints для администрирования
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from database import get_db, User, Tariff, TariffType, WorkoutCoefficients
from auth import get_current_admin_user
from schemas import (
    AdminUserResponse, UserTariffUpdate, TariffResponse, TariffsUpdateRequest,
    WorkoutCoefficientsResponse, WorkoutCoefficientsUpdate
)

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])

# Пользователи
@router.get("/users", response_model=List[AdminUserResponse])
async def get_all_users(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """Получить список всех пользователей"""
    users = db.query(User).all()
    
    result = []
    for user in users:
        tariff_type = None
        tariff_name = None
        if user.tariff:
            tariff_type = user.tariff.type
            tariff_name = user.tariff.name
        
        result.append(AdminUserResponse(
            id=user.id,
            uin=user.uin,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=bool(user.is_active),
            tariff_type=tariff_type,
            tariff_name=tariff_name,
            created_at=user.created_at
        ))
    
    return result

@router.put("/users/tariff")
async def update_user_tariff(
    request: UserTariffUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """Обновить тариф пользователя"""
    # Найти пользователя
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    # Найти тариф
    tariff = db.query(Tariff).filter(Tariff.type == request.tariff_type).first()
    if not tariff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тариф не найден"
        )
    
    # Обновить тариф пользователя
    user.tariff_id = tariff.id
    user.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Тариф пользователя успешно обновлен"}

# Тарифы
@router.get("/tariffs", response_model=List[TariffResponse])
async def get_all_tariffs(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """Получить список всех тарифов"""
    tariffs = db.query(Tariff).all()
    
    result = []
    for tariff in tariffs:
        result.append(TariffResponse(
            id=tariff.id,
            name=tariff.name,
            type=tariff.type,
            view_full_plan=bool(tariff.view_full_plan),
            view_two_weeks=bool(tariff.view_two_weeks),
            created_at=tariff.created_at,
            updated_at=tariff.updated_at
        ))
    
    return result

@router.put("/tariffs")
async def update_tariffs(
    request: TariffsUpdateRequest,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """Обновить настройки всех тарифов"""
    
    # Обновить тестовый тариф
    test_tariff = db.query(Tariff).filter(Tariff.type == TariffType.TEST).first()
    if test_tariff:
        test_tariff.view_full_plan = int(request.test.view_full_plan)
        test_tariff.view_two_weeks = int(request.test.view_two_weeks)
        test_tariff.updated_at = datetime.utcnow()
    
    # Обновить пробный тариф
    trial_tariff = db.query(Tariff).filter(Tariff.type == TariffType.TRIAL).first()
    if trial_tariff:
        trial_tariff.view_full_plan = int(request.trial.view_full_plan)
        trial_tariff.view_two_weeks = int(request.trial.view_two_weeks)
        trial_tariff.updated_at = datetime.utcnow()
    
    # Обновить про тариф
    pro_tariff = db.query(Tariff).filter(Tariff.type == TariffType.PRO).first()
    if pro_tariff:
        pro_tariff.view_full_plan = int(request.pro.view_full_plan)
        pro_tariff.view_two_weeks = int(request.pro.view_two_weeks)
        pro_tariff.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Настройки тарифов успешно обновлены"}

# Коэффициенты тренировок
@router.get("/workout-coefficients", response_model=WorkoutCoefficientsResponse)
async def get_workout_coefficients(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """Получить коэффициенты тренировок"""
    coefficients = db.query(WorkoutCoefficients).first()
    
    if not coefficients:
        # Создать коэффициенты по умолчанию, если их нет
        coefficients = WorkoutCoefficients()
        db.add(coefficients)
        db.commit()
        db.refresh(coefficients)
    
    return WorkoutCoefficientsResponse(
        id=coefficients.id,
        weekly_distance_beginner=coefficients.weekly_distance_beginner,
        weekly_distance_5_10=coefficients.weekly_distance_5_10,
        weekly_distance_10_30=coefficients.weekly_distance_10_30,
        weekly_distance_30_50=coefficients.weekly_distance_30_50,
        weekly_distance_50_plus=coefficients.weekly_distance_50_plus,
        pace_8_plus=coefficients.pace_8_plus,
        pace_7_8=coefficients.pace_7_8,
        pace_6_7=coefficients.pace_6_7,
        pace_5_6=coefficients.pace_5_6,
        pace_4_5=coefficients.pace_4_5,
        pace_4_minus=coefficients.pace_4_minus,
        target_distance_5k=coefficients.target_distance_5k,
        target_distance_10k=coefficients.target_distance_10k,
        target_distance_21k=coefficients.target_distance_21k,
        target_distance_42k=coefficients.target_distance_42k,
        time_preparation_base=coefficients.time_preparation_base,
        time_preparation_weeks_optimal=coefficients.time_preparation_weeks_optimal,
        created_at=coefficients.created_at,
        updated_at=coefficients.updated_at
    )

@router.put("/workout-coefficients")
async def update_workout_coefficients(
    request: WorkoutCoefficientsUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """Обновить коэффициенты тренировок"""
    coefficients = db.query(WorkoutCoefficients).first()
    
    if not coefficients:
        # Создать новые коэффициенты
        coefficients = WorkoutCoefficients()
        db.add(coefficients)
    
    # Обновить все коэффициенты
    coefficients.weekly_distance_beginner = request.weekly_distance_beginner
    coefficients.weekly_distance_5_10 = request.weekly_distance_5_10
    coefficients.weekly_distance_10_30 = request.weekly_distance_10_30
    coefficients.weekly_distance_30_50 = request.weekly_distance_30_50
    coefficients.weekly_distance_50_plus = request.weekly_distance_50_plus
    
    coefficients.pace_8_plus = request.pace_8_plus
    coefficients.pace_7_8 = request.pace_7_8
    coefficients.pace_6_7 = request.pace_6_7
    coefficients.pace_5_6 = request.pace_5_6
    coefficients.pace_4_5 = request.pace_4_5
    coefficients.pace_4_minus = request.pace_4_minus
    
    coefficients.target_distance_5k = request.target_distance_5k
    coefficients.target_distance_10k = request.target_distance_10k
    coefficients.target_distance_21k = request.target_distance_21k
    coefficients.target_distance_42k = request.target_distance_42k
    
    coefficients.time_preparation_base = request.time_preparation_base
    coefficients.time_preparation_weeks_optimal = request.time_preparation_weeks_optimal
    
    coefficients.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Коэффициенты тренировок успешно обновлены"}

# Проверка прав администратора
@router.get("/check-admin")
async def check_admin_rights(
    admin_user: User = Depends(get_current_admin_user)
):
    """Проверить права администратора"""
    return {
        "is_admin": True,
        "user_email": admin_user.email,
        "message": "Права администратора подтверждены"
    }
