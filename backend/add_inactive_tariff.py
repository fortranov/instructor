"""
Скрипт для добавления неактивного тарифа в существующую базу данных
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, Tariff, TariffType, ensure_database_compatibility, create_tables


def add_inactive_tariff():
    """Добавить неактивный тариф в базу данных"""
    
    # Инициализация базы данных
    ensure_database_compatibility()
    create_tables()
    
    db = SessionLocal()
    
    try:
        print("=" * 60)
        print("Добавление неактивного тарифа")
        print("=" * 60)
        
        # Проверяем, есть ли уже неактивный тариф
        inactive_tariff = db.query(Tariff).filter(Tariff.type == TariffType.INACTIVE).first()
        
        if inactive_tariff:
            print(f"✅ Неактивный тариф уже существует (ID: {inactive_tariff.id})")
            return True
        
        # Создаем неактивный тариф
        print("📝 Создание неактивного тарифа...")
        inactive_tariff = Tariff(
            name="Неактивный",
            type=TariffType.INACTIVE,
            view_full_plan=0,  # Не может просматривать весь план
            view_two_weeks=0   # Не может просматривать даже 2 недели
        )
        
        db.add(inactive_tariff)
        db.commit()
        db.refresh(inactive_tariff)
        
        print(f"✅ Неактивный тариф создан (ID: {inactive_tariff.id})")
        print("\n" + "=" * 60)
        print("✅ УСПЕШНО ЗАВЕРШЕНО")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
        
    finally:
        db.close()


if __name__ == "__main__":
    success = add_inactive_tariff()
    sys.exit(0 if success else 1)

