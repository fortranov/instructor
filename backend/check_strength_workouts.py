"""
Скрипт для проверки силовых тренировок в базе данных
"""

import sys
import os
from datetime import datetime

# Добавляем текущую директорию в PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, User, TrainingPlan, Workout, SportType
from sqlalchemy import func

def check_strength_workouts():
    """Проверить силовые тренировки для всех пользователей"""
    db = SessionLocal()

    try:
        print("=" * 80)
        print("ПРОВЕРКА СИЛОВЫХ ТРЕНИРОВОК")
        print("=" * 80)

        # Получить всех пользователей
        users = db.query(User).all()
        print(f"\nВсего пользователей: {len(users)}")

        for user in users:
            print(f"\n{'=' * 80}")
            print(f"Пользователь: {user.email}")
            print(f"UIN: {user.uin}")
            print(f"has_strength_training: {user.has_strength_training}")

            # Получить план пользователя
            plan = db.query(TrainingPlan).filter(TrainingPlan.user_id == user.id).first()

            if not plan:
                print("  ❌ План не найден")
                continue

            print(f"\nИнформация о плане:")
            print(f"  Дата соревнования: {plan.competition_date}")
            print(f"  Тип соревнования: {plan.competition_type}")
            print(f"  Сложность: {plan.complexity}")

            # Рассчитать фазу тренировки
            days_to_competition = (plan.competition_date - datetime.now().date()).days
            weeks_to_competition = max(1, days_to_competition // 7)

            if weeks_to_competition <= 2:
                phase = 'taper'
            elif weeks_to_competition <= 4:
                phase = 'peak'
            elif weeks_to_competition <= 8:
                phase = 'build'
            else:
                phase = 'base'

            print(f"  Недель до соревнования: {weeks_to_competition}")
            print(f"  Текущая фаза: {phase}")
            print(f"  Силовые тренировки доступны в фазах: base, build")
            print(f"  Силовые должны генерироваться: {phase in ['base', 'build']}")

            # Получить все тренировки пользователя
            workouts = db.query(Workout).filter(Workout.plan_id == plan.id).all()

            # Подсчитать количество тренировок по типам спорта
            sport_counts = db.query(
                Workout.sport_type,
                func.count(Workout.id)
            ).filter(
                Workout.plan_id == plan.id
            ).group_by(
                Workout.sport_type
            ).all()

            print(f"\nКоличество тренировок по видам спорта:")
            for sport_type, count in sport_counts:
                print(f"  {sport_type}: {count}")

            # Найти силовые тренировки
            strength_workouts = [w for w in workouts if w.sport_type == SportType.STRENGTH]

            print(f"\n{'=' * 40}")
            if strength_workouts:
                print(f"✅ Найдено силовых тренировок: {len(strength_workouts)}")
                print(f"\nПервые 5 силовых тренировок:")
                for i, workout in enumerate(strength_workouts[:5], 1):
                    print(f"  {i}. Дата: {workout.date}, Длительность: {workout.duration_minutes} мин, Тип: {workout.workout_type}")
            else:
                print(f"❌ Силовые тренировки НЕ найдены!")

                if not user.has_strength_training:
                    print(f"  Причина: has_strength_training = False")
                elif phase not in ['base', 'build']:
                    print(f"  Причина: текущая фаза '{phase}' не входит в base/build")
                else:
                    print(f"  Причина: неизвестна (возможно, проблема с генерацией)")

        print("\n" + "=" * 80)
        print("ПРОВЕРКА ЗАВЕРШЕНА")
        print("=" * 80)

    finally:
        db.close()

if __name__ == "__main__":
    check_strength_workouts()
