#!/usr/bin/env python3
"""
Скрипт для исправления проблем с тарифами
Создает таблицу тарифов, колонку tariff_id в users и тарифы по умолчанию
"""

from database import SessionLocal, Tariff, TariffType, User, Base, engine
import sys
from sqlalchemy import text

def fix_tariffs():
    """Исправить проблемы с тарифами"""
    
    print("🔧 Исправление тарифов...")
    
    try:
        # Создаем все таблицы, если их нет
        print("📋 Создание таблиц...")
        Base.metadata.create_all(bind=engine)
        print("✅ Таблицы проверены/созданы")
        
        db = SessionLocal()
        try:
            # Проверяем колонку tariff_id в таблице users
            print("🔍 Проверка колонки tariff_id в таблице users...")
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
            
            # Проверяем, есть ли тарифы
            tariffs_count = db.query(Tariff).count()
            print(f"📊 Найдено тарифов: {tariffs_count}")
            
            if tariffs_count == 0:
                print("⚙️ Создание тарифов по умолчанию...")
                
                tariffs_data = [
                    {
                        "name": "Тестовый",
                        "type": TariffType.TEST,
                        "view_full_plan": 0,  # Не может просматривать весь план
                        "view_two_weeks": 1   # Может просматривать 2 недели
                    },
                    {
                        "name": "Пробный", 
                        "type": TariffType.TRIAL,
                        "view_full_plan": 0,  # Не может просматривать весь план
                        "view_two_weeks": 1   # Может просматривать 2 недели
                    },
                    {
                        "name": "Про",
                        "type": TariffType.PRO,
                        "view_full_plan": 1,  # Может просматривать весь план
                        "view_two_weeks": 1   # Может просматривать 2 недели
                    }
                ]
                
                for tariff_data in tariffs_data:
                    tariff = Tariff(**tariff_data)
                    db.add(tariff)
                
                db.commit()
                print("✅ Тарифы созданы успешно")
                
                # Показываем созданные тарифы
                tariffs = db.query(Tariff).all()
                for tariff in tariffs:
                    print(f"   • {tariff.name} ({tariff.type}) - ID: {tariff.id}")
            else:
                print("✅ Тарифы уже существуют")
                tariffs = db.query(Tariff).all()
                for tariff in tariffs:
                    print(f"   • {tariff.name} ({tariff.type}) - ID: {tariff.id}")
            
            # Проверяем пользователей без тарифа
            users_without_tariff = db.query(User).filter(User.tariff_id.is_(None)).count()
            print(f"👥 Пользователей без тарифа: {users_without_tariff}")
            
            if users_without_tariff > 0:
                # Назначаем тестовый тариф пользователям без тарифа
                test_tariff = db.query(Tariff).filter(Tariff.type == TariffType.TEST).first()
                if test_tariff:
                    db.execute(
                        text("UPDATE users SET tariff_id = :tariff_id WHERE tariff_id IS NULL"),
                        {"tariff_id": test_tariff.id}
                    )
                    db.commit()
                    print(f"✅ Назначен тестовый тариф {users_without_tariff} пользователям")
            
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
    success = fix_tariffs()
    if success:
        print("🎉 Исправление тарифов завершено успешно!")
        sys.exit(0)
    else:
        print("💥 Исправление завершилось с ошибками!")
        sys.exit(1)
