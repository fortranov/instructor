"""
Управление тарифами пользователей и автоматический переход на неактивный тариф
"""

from datetime import datetime
from sqlalchemy.orm import Session
from database import User, Tariff, TariffType


def check_and_update_expired_test_tariff(db: Session, user: User) -> User:
    """
    Проверить и обновить тариф пользователя, если тестовый период истек.
    
    Если у пользователя тестовый тариф и дата окончания тестового периода прошла,
    автоматически переводит пользователя на неактивный тариф.
    
    Args:
        db: Сессия базы данных
        user: Пользователь для проверки
        
    Returns:
        Обновленный объект пользователя
    """
    # Проверяем только пользователей с тестовым тарифом
    if not user.tariff or user.tariff.type != TariffType.TEST:
        return user
    
    # Проверяем, установлена ли дата окончания тестового периода
    if not user.test_period_end_date:
        return user
    
    # Проверяем, истек ли тестовый период
    now = datetime.utcnow()
    if now < user.test_period_end_date:
        return user  # Тестовый период еще не истек
    
    # Тестовый период истек - переводим на неактивный тариф
    inactive_tariff = db.query(Tariff).filter(Tariff.type == TariffType.INACTIVE).first()
    
    if inactive_tariff:
        user.tariff_id = inactive_tariff.id
        user.updated_at = now
        db.commit()
        db.refresh(user)
        print(f"Пользователь {user.email} автоматически переведен на неактивный тариф")
    
    return user


def get_test_period_days_remaining(user: User) -> int | None:
    """
    Получить количество дней, оставшихся до конца тестового периода.
    
    Args:
        user: Пользователь
        
    Returns:
        Количество дней до конца тестового периода или None, если не применимо
    """
    # Проверяем только пользователей с тестовым тарифом
    if not user.tariff or user.tariff.type != TariffType.TEST:
        return None
    
    # Проверяем, установлена ли дата окончания
    if not user.test_period_end_date:
        return None
    
    # Вычисляем количество оставшихся дней
    now = datetime.utcnow()
    delta = user.test_period_end_date - now
    days_remaining = delta.days
    
    # Если дней отрицательное значение, тестовый период истек
    if days_remaining < 0:
        return 0
    
    return days_remaining


def update_user_tariff(db: Session, user: User, new_tariff_type: TariffType) -> User:
    """
    Обновить тариф пользователя.
    
    Args:
        db: Сессия базы данных
        user: Пользователь
        new_tariff_type: Новый тип тарифа
        
    Returns:
        Обновленный объект пользователя
    """
    new_tariff = db.query(Tariff).filter(Tariff.type == new_tariff_type).first()
    
    if not new_tariff:
        raise ValueError(f"Тариф {new_tariff_type} не найден в базе данных")
    
    user.tariff_id = new_tariff.id
    user.updated_at = datetime.utcnow()
    
    # Если переводим на тестовый тариф, устанавливаем дату окончания
    if new_tariff_type == TariffType.TEST:
        from datetime import timedelta
        user.test_period_end_date = datetime.utcnow() + timedelta(days=14)
    else:
        # Для других тарифов очищаем дату окончания тестового периода
        user.test_period_end_date = None
    
    db.commit()
    db.refresh(user)
    
    return user

