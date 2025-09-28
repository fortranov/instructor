"""
Скрипт для инициализации данных администрирования
Создает тарифы по умолчанию и пользователя-администратора
"""

from sqlalchemy.orm import Session
from database import SessionLocal, Tariff, TariffType, WorkoutCoefficients, User
from auth import get_password_hash
import uuid

def init_tariffs(db: Session):
    """Инициализация тарифов по умолчанию"""
    
    # Проверяем, есть ли уже тарифы
    existing_tariffs = db.query(Tariff).count()
    if existing_tariffs > 0:
        print("Тарифы уже существуют, пропускаем инициализацию")
        return
    
    # Создаем тарифы по умолчанию
    tariffs = [
        Tariff(
            name="Тестовый",
            type=TariffType.TEST,
            view_full_plan=0,  # Не может просматривать весь план
            view_two_weeks=1   # Может просматривать только 2 недели
        ),
        Tariff(
            name="Пробный", 
            type=TariffType.TRIAL,
            view_full_plan=0,  # Не может просматривать весь план
            view_two_weeks=1   # Может просматривать только 2 недели
        ),
        Tariff(
            name="Про",
            type=TariffType.PRO,
            view_full_plan=1,  # Может просматривать весь план
            view_two_weeks=1   # Может просматривать 2 недели
        )
    ]
    
    for tariff in tariffs:
        db.add(tariff)
    
    db.commit()
    print("Тарифы успешно созданы")

def init_workout_coefficients(db: Session):
    """Инициализация коэффициентов тренировок по умолчанию"""
    
    # Проверяем, есть ли уже коэффициенты
    existing_coefficients = db.query(WorkoutCoefficients).first()
    if existing_coefficients:
        print("Коэффициенты тренировок уже существуют, пропускаем инициализацию")
        return
    
    # Создаем коэффициенты по умолчанию (из plan_wizard.py)
    coefficients = WorkoutCoefficients(
        # Коэффициенты для недельного километража
        weekly_distance_beginner=10,
        weekly_distance_5_10=50,
        weekly_distance_10_30=100,
        weekly_distance_30_50=200,
        weekly_distance_50_plus=300,
        
        # Коэффициенты для комфортного темпа
        pace_8_plus=20,
        pace_7_8=50,
        pace_6_7=100,
        pace_5_6=150,
        pace_4_5=200,
        pace_4_minus=300,
        
        # Коэффициенты для целевой дистанции
        target_distance_5k=50,
        target_distance_10k=100,
        target_distance_21k=150,
        target_distance_42k=250,
        
        # Коэффициенты для времени подготовки
        time_preparation_base=100,
        time_preparation_weeks_optimal=16
    )
    
    db.add(coefficients)
    db.commit()
    print("Коэффициенты тренировок успешно созданы")

def init_admin_user(db: Session):
    """Инициализация пользователя-администратора"""
    
    # Проверяем, есть ли уже администратор
    admin_user = db.query(User).filter(User.email == "administrator").first()
    if admin_user:
        print("Пользователь-администратор уже существует")
        return
    
    # Создаем администратора
    admin_uin = str(uuid.uuid4())
    while db.query(User).filter(User.uin == admin_uin).first():
        admin_uin = str(uuid.uuid4())
    
    admin_user = User(
        uin=admin_uin,
        email="administrator",
        hashed_password=get_password_hash("admin123"),  # Пароль по умолчанию
        first_name="Администратор",
        last_name="Системы",
        is_active=1
    )
    
    db.add(admin_user)
    db.commit()
    print("Пользователь-администратор создан (email: administrator, пароль: admin123)")

def main():
    """Основная функция инициализации"""
    db = SessionLocal()
    try:
        print("Инициализация данных администрирования...")
        
        init_tariffs(db)
        init_workout_coefficients(db)
        init_admin_user(db)
        
        print("Инициализация завершена успешно!")
        
    except Exception as e:
        print(f"Ошибка при инициализации: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
