"""
Скрипт инициализации базы данных для продакшена
Создает все таблицы и заполняет их начальными данными
"""

from database import create_tables, SessionLocal, Tariff, TariffType, WorkoutCoefficients, User
from auth import get_password_hash
import uuid

def init_production_database():
    """Инициализация базы данных для продакшена"""
    
    print("🚀 Инициализация базы данных для продакшена...")
    
    # 1. Создаем все таблицы
    print("📋 Создание таблиц...")
    create_tables()
    print("✅ Таблицы созданы")
    
    db = SessionLocal()
    try:
        # 2. Создаем тарифы по умолчанию
        print("💳 Создание тарифов...")
        existing_tariffs = db.query(Tariff).count()
        if existing_tariffs == 0:
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
            print("✅ Тарифы созданы: Тестовый, Пробный, Про")
        else:
            print("✅ Тарифы уже существуют")
        
        # 3. Создаем коэффициенты тренировок по умолчанию
        print("⚙️ Создание коэффициентов тренировок...")
        existing_coefficients = db.query(WorkoutCoefficients).first()
        if not existing_coefficients:
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
            print("✅ Коэффициенты тренировок созданы")
        else:
            print("✅ Коэффициенты тренировок уже существуют")
        
        # 4. Создаем пользователя-администратора
        print("👤 Создание пользователя-администратора...")
        admin_user = db.query(User).filter(User.email == "abramov.yu.v@gmail.com").first()
        if not admin_user:
            admin_uin = str(uuid.uuid4())
            while db.query(User).filter(User.uin == admin_uin).first():
                admin_uin = str(uuid.uuid4())
            
            admin_user = User(
                uin=admin_uin,
                email="abramov.yu.v@gmail.com",
                hashed_password=get_password_hash("admin123"),  # Пароль по умолчанию
                first_name="Юрий",
                last_name="Абрамов",
                is_active=1
            )
            
            db.add(admin_user)
            db.commit()
            print("✅ Пользователь-администратор создан")
            print("   📧 Email: abramov.yu.v@gmail.com")
            print("   🔑 Пароль: admin123")
            print("   ⚠️  ВАЖНО: Смените пароль после первого входа!")
        else:
            print("✅ Пользователь-администратор уже существует")
        
        print("\n🎉 Инициализация базы данных завершена успешно!")
        print("\n📋 Что создано:")
        print("   • Все необходимые таблицы")
        print("   • 3 тарифных плана (Тестовый, Пробный, Про)")
        print("   • Коэффициенты для расчета планов тренировок")
        print("   • Пользователь-администратор")
        print("\n🚀 База данных готова к работе!")
        
    except Exception as e:
        print(f"❌ Ошибка при инициализации: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_production_database()
