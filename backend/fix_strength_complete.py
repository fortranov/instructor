"""
Комплексное исправление силовых тренировок:
1. Установить has_strength_training=1 для пользователей с планами
2. Добавить силовые тренировки (даже в занятые дни)
"""

import sys
import os
from datetime import datetime, timedelta, date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, User, TrainingPlan, Workout, SportType, WorkoutType, CompetitionType

def fix_strength_complete():
    """Комплексное исправление силовых тренировок"""
    db = SessionLocal()

    try:
        print("=" * 80)
        print("КОМПЛЕКСНОЕ ИСПРАВЛЕНИЕ СИЛОВЫХ ТРЕНИРОВОК")
        print("=" * 80)

        # ШАГ 1: Установить has_strength_training=1 для пользователей с планами триатлона
        print("\n" + "=" * 80)
        print("ШАГ 1: Проверка и обновление has_strength_training")
        print("=" * 80)

        triathlon_types = [
            CompetitionType.TRIATHLON_SPRINT,
            CompetitionType.TRIATHLON_OLYMPIC,
            CompetitionType.TRIATHLON_IRONMAN
        ]

        users_with_plans = db.query(User).join(
            TrainingPlan, User.id == TrainingPlan.user_id
        ).all()

        for user in users_with_plans:
            plan = db.query(TrainingPlan).filter(TrainingPlan.user_id == user.id).first()

            print(f"\n{user.email}:")
            print(f"  Тип соревнования: {plan.competition_type}")
            print(f"  has_strength_training (до): {user.has_strength_training}")

            # Для триатлона включаем силовые по умолчанию
            if plan.competition_type in triathlon_types and not user.has_strength_training:
                user.has_strength_training = 1
                db.commit()
                print(f"  has_strength_training (после): 1 ✅ ОБНОВЛЕНО")
            else:
                print(f"  has_strength_training (после): {user.has_strength_training} (без изменений)")

        # ШАГ 2: Добавить силовые тренировки
        print("\n" + "=" * 80)
        print("ШАГ 2: Добавление силовых тренировок")
        print("=" * 80)

        users_for_strength = db.query(User).join(
            TrainingPlan, User.id == TrainingPlan.user_id
        ).filter(User.has_strength_training == 1).all()

        print(f"\nПользователей с has_strength_training=1: {len(users_for_strength)}")

        for user in users_for_strength:
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

            today = date.today()
            current_week_start = today - timedelta(days=today.weekday())

            added_count = 0
            checked_weeks = 0

            while current_week_start < plan.competition_date and checked_weeks < 52:
                checked_weeks += 1
                week_end = current_week_start + timedelta(days=7)

                # Рассчитать фазу
                weeks_remaining = max(1, (plan.competition_date - current_week_start).days // 7)

                if weeks_remaining <= 2:
                    week_phase = 'taper'
                elif weeks_remaining <= 4:
                    week_phase = 'peak'
                elif weeks_remaining <= 8:
                    week_phase = 'build'
                else:
                    week_phase = 'base'

                # Только в base/build/peak
                if week_phase not in ['base', 'build', 'peak']:
                    current_week_start += timedelta(days=7)
                    continue

                # Тренировки этой недели
                week_workouts = db.query(Workout).filter(
                    Workout.plan_id == plan.id,
                    Workout.date >= current_week_start,
                    Workout.date < week_end
                ).all()

                if not week_workouts:
                    current_week_start += timedelta(days=7)
                    continue

                # Проверить, есть ли уже силовая
                has_strength_this_week = any(w.sport_type == SportType.STRENGTH for w in week_workouts)
                if has_strength_this_week:
                    current_week_start += timedelta(days=7)
                    continue

                # Найти тренировки по дням
                workouts_by_day = {}
                for w in week_workouts:
                    day = w.date.weekday()
                    if day not in workouts_by_day:
                        workouts_by_day[day] = []
                    workouts_by_day[day].append(w)

                # Найти подходящий день
                strength_date = None

                # Стратегия 1: Свободный день
                for day in preferred_days:
                    candidate_date = current_week_start + timedelta(days=day)
                    if candidate_date >= today and candidate_date < plan.competition_date:
                        if day not in workouts_by_day:
                            strength_date = candidate_date
                            break

                # Стратегия 2: День с минимальной нагрузкой
                if not strength_date:
                    min_duration = float('inf')
                    for day in preferred_days:
                        candidate_date = current_week_start + timedelta(days=day)
                        if candidate_date < today or candidate_date >= plan.competition_date:
                            continue
                        day_duration = sum(w.duration_minutes for w in workouts_by_day.get(day, []))
                        if day_duration < min_duration:
                            min_duration = day_duration
                            strength_date = candidate_date

                # Добавить силовую
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

                    if strength_date.weekday() in workouts_by_day:
                        day_info = f"день с {len(workouts_by_day[strength_date.weekday()])} тренировкой(ами)"
                    else:
                        day_info = "свободный день"

                    if added_count <= 5:  # Показываем первые 5
                        print(f"  + {strength_date} ({week_phase}, {day_info})")

                current_week_start += timedelta(days=7)

            if added_count > 0:
                db.commit()
                print(f"\n✅ УСПЕШНО ДОБАВЛЕНО {added_count} силовых тренировок!")
            else:
                print(f"\n⚠️  Не удалось добавить силовые")

        print("\n" + "=" * 80)
        print("ГОТОВО!")
        print("=" * 80)
        print("\nТеперь обновите страницу в браузере (Ctrl+F5)")

    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_strength_complete()
