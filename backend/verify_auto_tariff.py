"""
Скрипт для проверки автоматического назначения тестового тарифа
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, User, Tariff, TariffType, create_tables, ensure_database_compatibility
from auth import create_user
import uuid


def verify_auto_tariff():
    """Проверка автоматического назначения тарифа"""
    
    ensure_database_compatibility()
    create_tables()
    
    db = SessionLocal()
    test_user = None
    
    try:
        print("\n" + "=" * 60)
        print("ПРОВЕРКА: Автоматическое назначение тестового тарифа")
        print("=" * 60 + "\n")
        
        # 1. Проверка наличия тестового тарифа
        print("1️⃣  Проверка наличия тестового тарифа...")
        test_tariff = db.query(Tariff).filter(Tariff.type == TariffType.TEST).first()
        
        if not test_tariff:
            print("   ❌ Тестовый тариф не найден!")
            print("   ℹ️  Запустите: python backend/init_admin_data.py")
            return False
        
        print(f"   ✅ Тариф найден: '{test_tariff.name}' (ID: {test_tariff.id})")
        print(f"      • Просмотр всего плана: {'Да' if test_tariff.view_full_plan else 'Нет'}")
        print(f"      • Просмотр двух недель: {'Да' if test_tariff.view_two_weeks else 'Нет'}\n")
        
        # 2. Создание тестового пользователя
        print("2️⃣  Создание тестового пользователя...")
        test_email = f"verify_{uuid.uuid4().hex[:8]}@test.local"
        
        test_user = create_user(
            db=db,
            email=test_email,
            password="test123",
            first_name="Проверка",
            last_name="Тарифов"
        )
        
        print(f"   ✅ Пользователь создан")
        print(f"      • Email: {test_email}")
        print(f"      • UIN: {test_user.uin}\n")
        
        # 3. Проверка назначения тарифа
        print("3️⃣  Проверка назначения тарифа...")
        
        if not test_user.tariff_id:
            print("   ❌ Тариф НЕ назначен!")
            return False
        
        print(f"   ✅ Тариф назначен (ID: {test_user.tariff_id})")
        
        # 4. Проверка корректности тарифа
        print("\n4️⃣  Проверка корректности тарифа...")
        db.refresh(test_user)
        
        if not test_user.tariff:
            print("   ❌ Не удалось загрузить данные тарифа")
            return False
        
        if test_user.tariff.type != TariffType.TEST:
            print(f"   ❌ Назначен неправильный тариф: {test_user.tariff.type}")
            return False
        
        print(f"   ✅ Назначен правильный тариф: '{test_user.tariff.name}'")
        print(f"      • Тип: {test_user.tariff.type}")
        
        # Успех!
        print("\n" + "=" * 60)
        print("✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ УСПЕШНО!")
        print("=" * 60)
        print("\nТестовый тариф автоматически назначается")
        print("при регистрации новых пользователей.\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Очистка
        if test_user:
            try:
                print("🧹 Удаление тестового пользователя...")
                db.delete(test_user)
                db.commit()
                print("✅ Тестовый пользователь удалён\n")
            except Exception as e:
                print(f"⚠️  Ошибка при удалении: {e}\n")
        
        db.close()


if __name__ == "__main__":
    success = verify_auto_tariff()
    sys.exit(0 if success else 1)

