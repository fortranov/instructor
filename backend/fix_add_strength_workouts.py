"""
Скрипт для диагностики и добавления силовых тренировок в существующие планы
"""

import sys
import os
from datetime import datetime, timedelta, date

# Добавляем текущую директорию в PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, User, TrainingPlan, Workout, SportType, WorkoutType
from sqlalchemy import func

def diagnose_and_fix_strength_workouts():
    """Диагностировать и исправить проблему с силовыми тренировками"""
    db = SessionLocal()

    try:
        print("=" * 80)
        print("ДИАГНОСТИКА И ИСПРАВЛЕНИЕ СИЛОВЫХ ТРЕНИРОВОК")
        print("=" * 80)

        # Получить всех пользователей с планами
        users = db.query(User).join(TrainingPlan, User.id == TrainingPlan.user_id).all()
        print(f"\nПользователей с планами: {len(users)}")

        for user in users:
            print(f"\n{'=' * 80}")
            print(f"Пользователь: {user.email}")
            print(f"UIN: {user.uin}")
            print(f"has_strength_training (тип: {type(user.has_strength_training)}): {user.has_strength_training}")

            # ВАЖНО: Проверяем значение как bool
            has_strength = bool(user.has_strength_training)
            print(f"has_strength_training (bool): {has_strength}")

            # Получить план пользователя
            plan = db.query(TrainingPlan).filter(TrainingPlan.user_id == user.id).first()

            if not plan:
                print("  ❌ План не найден")
                continue

            print(f"\nИнформация о плане:")
            print(f"  ID плана: {plan.id}")
            print(f"  Дата соревнования: {plan.competition_date}")
            print(f"  Тип соревнования: {plan.competition_type}")
            print(f"  Сложность: {plan.complexity}")

            # Рассчитать фазу тренировки
            today = date.today()
            days_to_competition = (plan.competition_date - today).days
            weeks_to_competition = max(1, days_to_competition // 7)

            if weeks_to_competition <= 2:
                phase = 'taper'
            elif weeks_to_competition <= 4:
                phase = 'peak'
            elif weeks_to_competition <= 8:
                phase = 'build'
            else:
                phase = 'base'

            print(f"  Дней до соревнования: {days_to_competition}")
            print(f"  Недель до соревнования: {weeks_to_competition}")
            print(f"  Текущая фаза: {phase}")

            # Получить все тренировки
            all_workouts = db.query(Workout).filter(Workout.plan_id == plan.id).all()
            strength_workouts = [w for w in all_workouts if w.sport_type == SportType.STRENGTH]

            print(f"\nТекущее состояние:")
            print(f"  Всего тренировок: {len(all_workouts)}")
            print(f"  Силовых тренировок: {len(strength_workouts)}")

            # Проверка условий для добавления силовых
            print(f"\nПроверка условий:")
            print(f"  ✓ has_strength_training = {has_strength} {'✓' if has_strength else '✗'}")
            print(f"  ✓ phase in ['base', 'build', 'peak'] = {phase in ['base', 'build', 'peak']} {'✓' if phase in ['base', 'build', 'peak'] else '✗'}")
            should_have_strength = has_strength and phase in ['base', 'build', 'peak']
            print(f"  → Должны быть силовые: {should_have_strength}")

            if not should_have_strength:
                print(f"\n⚠️  Силовые тренировки НЕ должны добавляться:")
                if not has_strength:
                    print(f"    - has_strength_training = False")
                if phase not in ['base', 'build', 'peak']:
                    print(f"    - Фаза '{phase}' не входит в base/build/peak")
                continue

            if len(strength_workouts) > 0:
                print(f"\n✅ Силовые тренировки уже есть ({len(strength_workouts)} шт)")
                continue

            # ДОБАВЛЯЕМ СИЛОВЫЕ ТРЕНИРОВКИ
            print(f"\n🔧 ДОБАВЛЕНИЕ СИЛОВЫХ ТРЕНИРОВОК...")

            # Получить предпочтительные дни
            try:
                import json
                preferred_days = json.loads(user.preferred_workout_days) if user.preferred_workout_days else [0, 1, 2, 3, 4, 5, 6]
            except:
                preferred_days = [0, 1, 2, 3, 4, 5, 6]

            print(f"  Предпочтительные дни: {preferred_days}")

            # Проходим по неделям плана и добавляем силовые
            added_count = 0
            current_week_start = today - timedelta(days=today.weekday())  # Понедельник текущей недели

            while current_week_start < plan.competition_date:
                # Рассчитываем фазу для этой недели
                weeks_remaining = max(1, (plan.competition_date - current_week_start).days // 7)

                if weeks_remaining <= 2:
                    week_phase = 'taper'
                elif weeks_remaining <= 4:
                    week_phase = 'peak'
                elif weeks_remaining <= 8:
                    week_phase = 'build'
                else:
                    week_phase = 'base'

                # Добавляем силовую только в нужных фазах
                if week_phase in ['base', 'build', 'peak']:
                    # Получить тренировки этой недели
                    week_end = current_week_start + timedelta(days=7)
                    week_workouts = db.query(Workout).filter(
                        Workout.plan_id == plan.id,
                        Workout.date >= current_week_start,
                        Workout.date < week_end
                    ).all()

                    # Найти занятые дни недели
                    occupied_days = set([w.date.weekday() for w in week_workouts])

                    # Найти свободный предпочтительный день
                    for day in preferred_days:
                        if day not in occupied_days:
                            workout_date = current_week_start + timedelta(days=day)

                            # Проверить, что дата не в прошлом и не после соревнования
                            if workout_date >= today and workout_date < plan.competition_date:
                                # Создать силовую тренировку
                                strength_workout = Workout(
                                    plan_id=plan.id,
                                    date=workout_date,
                                    sport_type=SportType.STRENGTH,
                                    duration_minutes=50,
                                    workout_type=WorkoutType.RECOVERY
                                )
                                db.add(strength_workout)
                                added_count += 1
                                print(f"    + Добавлена силовая на {workout_date} ({week_phase})")
                                break

                # Переходим к следующей неделе
                current_week_start += timedelta(days=7)

            if added_count > 0:
                db.commit()
                print(f"\n✅ Успешно добавлено {added_count} силовых тренировок!")
            else:
                print(f"\n⚠️  Не удалось добавить силовые тренировки (возможно, нет свободных дней)")

        print("\n" + "=" * 80)
        print("ДИАГНОСТИКА И ИСПРАВЛЕНИЕ ЗАВЕРШЕНЫ")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    diagnose_and_fix_strength_workouts()
