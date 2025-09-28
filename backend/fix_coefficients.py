#!/usr/bin/env python3
"""
Скрипт для исправления проблем с коэффициентами тренировок
Создает таблицу и коэффициенты, если их нет
"""

from database import SessionLocal, WorkoutCoefficients, Base, engine
import sys

def fix_workout_coefficients():
    """Исправить проблемы с коэффициентами тренировок"""
    
    print("🔧 Исправление коэффициентов тренировок...")
    
    try:
        # Создаем все таблицы, если их нет
        print("📋 Создание таблиц...")
        Base.metadata.create_all(bind=engine)
        print("✅ Таблицы проверены/созданы")
        
        db = SessionLocal()
        try:
            # Проверяем, есть ли коэффициенты
            coefficients = db.query(WorkoutCoefficients).first()
            
            if coefficients:
                print("✅ Коэффициенты уже существуют")
                print(f"   ID: {coefficients.id}")
                print(f"   Недельный километраж (новичок): {coefficients.weekly_distance_beginner}")
                return True
            
            print("⚙️ Создание коэффициентов по умолчанию...")
            
            # Создаем коэффициенты по умолчанию
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
            db.refresh(coefficients)
            
            print("✅ Коэффициенты созданы успешно")
            print(f"   ID: {coefficients.id}")
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
    success = fix_workout_coefficients()
    if success:
        print("🎉 Исправление завершено успешно!")
        sys.exit(0)
    else:
        print("💥 Исправление завершилось с ошибками!")
        sys.exit(1)
