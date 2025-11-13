"""
Скрипт для принудительного добавления силовых тренировок
Добавляет силовые даже если день уже занят (нормально для триатлона)
"""

import sys
import os
from datetime import datetime, timedelta, date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, User, TrainingPlan, Workout, SportType, WorkoutType
from sqlalchemy import func

def add_strength_workouts_force():
    """Принудительно добавить силовые тренировки"""
    db = SessionLocal()

    try:
        print("=" * 80)
        print("ДОБАВЛЕНИЕ СИЛОВЫХ ТРЕНИРОВОК (ПРИНУДИТЕЛЬНО)")
        print("=" * 80)

        # Получить всех пользователей с has_strength_training = True
        users = db.query(User).join(TrainingPlan, User.id == TrainingPlan.user_id).filter(
            User.has_strength_training == 1
        ).all()

        print(f"\nПользователей с has_strength_training=True: {len(users)}")

        for user in users:
            print(f"\n{'=' * 80}")
            print(f"Пользователь: {user.email}")

            plan = db.query(TrainingPlan).filter(TrainingPlan.user_id == user.id).first()
            if not plan:
                continue

            # Проверить текущее количество силовых
            existing_strength = db.query(Workout).filter(
                Workout.plan_id == plan.id,
                Workout.sport_type == SportType.STRENGTH
            ).count()

            print(f"Силовых тренировок сейчас: {existing_strength}")

            if existing_strength > 0:
                print("✅ Силовые уже есть, пропускаем")
                continue

            # Получить предпочтительные дни
            try:
                import json
                preferred_days = json.loads(user.preferred_workout_days) if user.preferred_workout_days else [0, 1, 2, 3, 4, 5, 6]
            except:
                preferred_days = [0, 1, 2, 3, 4, 5, 6]

            print(f"Предпочтительные дни: {preferred_days}")

            # Получить все тренировки плана, сгруппированные по неделям
            today = date.today()
            current_week_start = today - timedelta(days=today.weekday())

            added_count = 0
            checked_weeks = 0

            while current_week_start < plan.competition_date and checked_weeks < 52:  # Максимум 52 недели
                checked_weeks += 1
                week_end = current_week_start + timedelta(days=7)

                # Рассчитать фазу для этой недели
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
                if week_phase not in ['base', 'build', 'peak']:
                    current_week_start += timedelta(days=7)
                    continue

                # Получить тренировки этой недели
                week_workouts = db.query(Workout).filter(
                    Workout.plan_id == plan.id,
                    Workout.date >= current_week_start,
                    Workout.date < week_end
                ).all()

                # Если в неделе нет тренировок, пропускаем
                if not week_workouts:
                    current_week_start += timedelta(days=7)
                    continue

                # Проверить, есть ли уже силовая на этой неделе
                has_strength_this_week = any(w.sport_type == SportType.STRENGTH for w in week_workouts)
                if has_strength_this_week:
                    current_week_start += timedelta(days=7)
                    continue

                # Найти тренировки по дням недели
                workouts_by_day = {}
                for w in week_workouts:
                    day = w.date.weekday()
                    if day not in workouts_by_day:
                        workouts_by_day[day] = []
                    workouts_by_day[day].append(w)

                # Стратегия 1: Попытаться найти свободный предпочтительный день
                strength_date = None
                for day in preferred_days:
                    candidate_date = current_week_start + timedelta(days=day)

                    # Проверить условия
                    if candidate_date < today or candidate_date >= plan.competition_date:
                        continue

                    # Если день свободен - идеально
                    if day not in workouts_by_day:
                        strength_date = candidate_date
                        break

                # Стратегия 2: Если все дни заняты, добавить в день с минимальным объемом
                if not strength_date:
                    # Найти день с минимальным суммарным временем тренировок
                    min_duration = float('inf')
                    best_day = None

                    for day in preferred_days:
                        candidate_date = current_week_start + timedelta(days=day)

                        if candidate_date < today or candidate_date >= plan.competition_date:
                            continue

                        # Суммарное время в этот день
                        day_duration = sum(w.duration_minutes for w in workouts_by_day.get(day, []))

                        # Найти день с минимальной нагрузкой
                        if day_duration < min_duration:
                            min_duration = day_duration
                            best_day = day
                            strength_date = candidate_date

                # Если нашли подходящую дату, добавляем силовую
                if strength_date:
                    strength_workout = Workout(
                        plan_id=plan.id,
                        date=strength_date,
                        sport_type=SportType.STRENGTH,
                        duration_minutes=50,
                        workout_type=WorkoutType.RECOVERY
                    )
                    db.add(strength_workout)
                    added_count += 1

                    day_info = "свободный день" if strength_date.weekday() not in workouts_by_day else f"день с {len(workouts_by_day[strength_date.weekday()])} тренировкой(ами)"
                    print(f"  + {strength_date} ({week_phase}, {day_info})")

                current_week_start += timedelta(days=7)

            if added_count > 0:
                db.commit()
                print(f"\n✅ УСПЕШНО ДОБАВЛЕНО {added_count} силовых тренировок!")
            else:
                print(f"\n⚠️  Не удалось добавить силовые (проверено {checked_weeks} недель)")

        print("\n" + "=" * 80)
        print("ЗАВЕРШЕНО")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_strength_workouts_force()
