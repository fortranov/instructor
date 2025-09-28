#!/usr/bin/env python3
"""
Универсальный скрипт для исправления всех проблем админки
Исправляет тарифы, коэффициенты и создает администратора
"""

from database import SessionLocal, Tariff, TariffType, User, WorkoutCoefficients, Base, engine
from auth import get_password_hash
import sys
import uuid
from sqlalchemy import text

def fix_all_admin_issues():
    """Исправить все проблемы админки"""
    
    print("🚀 Исправление всех проблем админки...")
    
    try:
        # Создаем все таблицы, если их нет
        print("📋 Создание таблиц...")
        Base.metadata.create_all(bind=engine)
        print("✅ Таблицы проверены/созданы")
        
        db = SessionLocal()
        try:
            # 1. Исправляем тарифы
            print("\n💳 Исправление тарифов...")
            
            # Проверяем колонку tariff_id в таблице users
            try:
                result = db.execute(text("PRAGMA table_info(users)"))
                columns = [row[1] for row in result.fetchall()]
                
                if 'tariff_id' not in columns:
                    print("➕ Добавление колонки tariff_id...")
                    db.execute(text("ALTER TABLE users ADD COLUMN tariff_id INTEGER"))
                    db.commit()
                    print("✅ Колонка tariff_id добавлена")
                else:
                    print("✅ Колонка tariff_id уже существует")
                    
            except Exception as column_error:
                print(f"⚠️ Ошибка проверки колонки: {column_error}")
            
            # Создаем тарифы
            tariffs_count = db.query(Tariff).count()
            if tariffs_count == 0:
                print("⚙️ Создание тарифов по умолчанию...")
                
                tariffs_data = [
                    {"name": "Тестовый", "type": TariffType.TEST, "view_full_plan": 0, "view_two_weeks": 1},
                    {"name": "Пробный", "type": TariffType.TRIAL, "view_full_plan": 0, "view_two_weeks": 1},
                    {"name": "Про", "type": TariffType.PRO, "view_full_plan": 1, "view_two_weeks": 1}
                ]
                
                for tariff_data in tariffs_data:
                    tariff = Tariff(**tariff_data)
                    db.add(tariff)
                
                db.commit()
                print("✅ Тарифы созданы")
            else:
                print("✅ Тарифы уже существуют")
            
            # Назначаем тариф пользователям без тарифа
            users_without_tariff = db.query(User).filter(User.tariff_id.is_(None)).count()
            if users_without_tariff > 0:
                test_tariff = db.query(Tariff).filter(Tariff.type == TariffType.TEST).first()
                if test_tariff:
                    db.execute(
                        text("UPDATE users SET tariff_id = :tariff_id WHERE tariff_id IS NULL"),
                        {"tariff_id": test_tariff.id}
                    )
                    db.commit()
                    print(f"✅ Назначен тестовый тариф {users_without_tariff} пользователям")
            
            # 2. Исправляем коэффициенты
            print("\n⚙️ Исправление коэффициентов...")
            
            coefficients = db.query(WorkoutCoefficients).first()
            if not coefficients:
                print("⚙️ Создание коэффициентов по умолчанию...")
                coefficients = WorkoutCoefficients(
                    weekly_distance_beginner=10,
                    weekly_distance_5_10=50,
                    weekly_distance_10_30=100,
                    weekly_distance_30_50=200,
                    weekly_distance_50_plus=300,
                    pace_8_plus=20,
                    pace_7_8=50,
                    pace_6_7=100,
                    pace_5_6=150,
                    pace_4_5=200,
                    pace_4_minus=300,
                    target_distance_5k=50,
                    target_distance_10k=100,
                    target_distance_21k=150,
                    target_distance_42k=250,
                    time_preparation_base=100,
                    time_preparation_weeks_optimal=16
                )
                db.add(coefficients)
                db.commit()
                print("✅ Коэффициенты созданы")
            else:
                print("✅ Коэффициенты уже существуют")
            
            # 3. Создаем администратора
            print("\n👤 Проверка администратора...")
            
            admin_user = db.query(User).filter(User.email == "abramov.yu.v@gmail.com").first()
            if not admin_user:
                print("⚙️ Создание пользователя-администратора...")
                admin_uin = str(uuid.uuid4())
                while db.query(User).filter(User.uin == admin_uin).first():
                    admin_uin = str(uuid.uuid4())
                
                admin_user = User(
                    uin=admin_uin,
                    email="abramov.yu.v@gmail.com",
                    hashed_password=get_password_hash("admin123"),
                    first_name="Юрий",
                    last_name="Абрамов",
                    is_active=1
                )
                db.add(admin_user)
                db.commit()
                print("✅ Администратор создан")
                print("   📧 Email: abramov.yu.v@gmail.com")
                print("   🔑 Пароль: admin123")
            else:
                print("✅ Администратор уже существует")
            
            print("\n📊 Итоговая статистика:")
            print(f"   • Тарифов: {db.query(Tariff).count()}")
            print(f"   • Пользователей: {db.query(User).count()}")
            print(f"   • Коэффициентов: {db.query(WorkoutCoefficients).count()}")
            
            return True
            
        except Exception as db_error:
            print(f"❌ Ошибка работы с БД: {db_error}")
            db.rollback()
            return False
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        return False

if __name__ == "__main__":
    success = fix_all_admin_issues()
    if success:
        print("\n🎉 Все проблемы админки исправлены успешно!")
        print("🔗 Теперь можно использовать админку на https://icanrun.ru/admin")
        sys.exit(0)
    else:
        print("\n💥 Исправление завершилось с ошибками!")
        sys.exit(1)
