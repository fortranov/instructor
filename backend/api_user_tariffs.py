"""
API endpoints для работы с тарифами пользователей
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db, User, Tariff, TariffType, AppSettings
from auth import get_current_active_user
from schemas import UserTariffResponse, TariffPurchaseRequest, TariffPriceResponse
from tariff_manager import check_and_update_expired_test_tariff, get_test_period_days_remaining

router = APIRouter(prefix="/api/v1/user", tags=["user-tariffs"])

@router.get("/tariff", response_model=UserTariffResponse)
async def get_user_tariff(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Получить информацию о тарифе текущего пользователя"""
    # Проверяем и обновляем тариф, если тестовый период истек
    current_user = check_and_update_expired_test_tariff(db, current_user)
    
    if current_user.tariff:
        # Получаем количество дней до конца тестового периода
        days_remaining = get_test_period_days_remaining(current_user)
        
        # Форматируем дату окончания тестового периода
        test_period_end = None
        if current_user.test_period_end_date:
            test_period_end = current_user.test_period_end_date.isoformat()
        
        return UserTariffResponse(
            tariff_type=current_user.tariff.type,
            tariff_name=current_user.tariff.name,
            test_period_days_remaining=days_remaining,
            test_period_end_date=test_period_end
        )
    else:
        return UserTariffResponse(
            tariff_type=None,
            tariff_name=None,
            test_period_days_remaining=None,
            test_period_end_date=None
        )

@router.get("/tariff/price")
async def get_tariff_price(
    months: int = 1,
    db: Session = Depends(get_db)
):
    """Получить цену тарифа Про с учетом скидок"""
    if months < 1 or months > 12:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Количество месяцев должно быть от 1 до 12"
        )
    
    # Получаем базовую цену из настроек
    price_setting = db.query(AppSettings).filter(AppSettings.key == "pro_tariff_price").first()
    if not price_setting:
        # Создаем настройку по умолчанию если её нет
        price_setting = AppSettings(
            key="pro_tariff_price",
            value="999.00",
            description="Цена тарифа Про за месяц (в рублях)"
        )
        db.add(price_setting)
        db.commit()
    
    base_price = float(price_setting.value)
    
    # Рассчитываем скидку
    discount_percent = 0
    if months == 2:
        discount_percent = 5
    elif months == 6:
        discount_percent = 10
    elif months == 12:
        discount_percent = 15
    
    # Рассчитываем итоговую цену
    total_without_discount = base_price * months
    discount_amount = total_without_discount * (discount_percent / 100)
    final_price = total_without_discount - discount_amount
    
    return TariffPriceResponse(
        base_price=base_price,
        months=months,
        discount_percent=discount_percent,
        final_price=final_price,
        total_savings=discount_amount
    )

@router.post("/tariff/purchase")
async def purchase_tariff(
    purchase_request: TariffPurchaseRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Покупка/продление тарифа (заглушка для интеграции с платежной системой)"""
    
    # Проверяем, что тариф существует
    tariff = db.query(Tariff).filter(Tariff.type == purchase_request.tariff_type).first()
    if not tariff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тариф не найден"
        )
    
    # Получаем информацию о цене
    price_info = await get_tariff_price(purchase_request.months, db)
    
    # Здесь должна быть интеграция с платежной системой
    # Пока просто возвращаем информацию о покупке
    
    return {
        "message": "Запрос на покупку тарифа создан",
        "tariff_type": purchase_request.tariff_type,
        "months": purchase_request.months,
        "price": price_info.final_price,
        "savings": price_info.total_savings,
        "note": "Это демо-версия. Интеграция с платежной системой не реализована."
    }
