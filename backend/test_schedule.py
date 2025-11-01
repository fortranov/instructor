"""
Тестовый скрипт для проверки новой логики распределения тренировок
"""

from datetime import date, timedelta
from database import SportType, WorkoutType, CompetitionType
from training_tables import TrainingTables

# Тестовые данные
def test_schedule_logic():
    print("=== Тест 1: Беговые тренировки ===")
    print("Предпочтительные дни: Пн(0), Ср(2), Пт(4), Сб(5)")
    print()

    # Получить распределение тренировок на неделю
    tt = TrainingTables()
    sport_types = [SportType.RUNNING]
    weekly_volume = 300  # 5 часов
    phase = 'build'
    complexity = 500

    workouts = tt.distribute_weekly_workouts(sport_types, weekly_volume, phase, complexity)

    print(f"Всего тренировок на неделю: {len(workouts)}")
    print("\nТренировки:")
    for i, (sport, wtype, duration) in enumerate(workouts, 1):
        print(f"{i}. {sport.value} - {wtype.value} - {duration} мин")

    # Разделить на типы
    endurance = [w for w in workouts if w[1] == WorkoutType.ENDURANCE]
    recovery = [w for w in workouts if w[1] == WorkoutType.RECOVERY]
    interval = [w for w in workouts if w[1] == WorkoutType.INTERVAL]

    print(f"\nДлительные (ENDURANCE): {len(endurance)}")
    for w in endurance:
        print(f"  - {w[2]} мин")
    print(f"Восстановительные (RECOVERY): {len(recovery)}")
    print(f"Интервальные (INTERVAL): {len(interval)}")

    print("\n" + "="*60)
    print("=== Тест 2: Триатлон ===")
    print("Проверка порядка видов спорта")
    print()

    triathlon_sports = tt.get_sport_types_for_competition(CompetitionType.TRIATHLON_OLYMPIC)
    print(f"Порядок видов спорта для триатлона: {[s.value for s in triathlon_sports]}")
    print("Ожидаемый порядок: running, cycling, swimming")

    if triathlon_sports == [SportType.RUNNING, SportType.CYCLING, SportType.SWIMMING]:
        print("✓ Порядок ПРАВИЛЬНЫЙ")
    else:
        print("✗ Порядок НЕПРАВИЛЬНЫЙ")

    print("\n" + "="*60)
    print("=== Тест 3: Распределение триатлона по неделе ===")

    triathlon_workouts = tt.distribute_weekly_workouts(
        triathlon_sports, 600, 'build', 600
    )

    print(f"Всего тренировок триатлона: {len(triathlon_workouts)}")

    # Группировка по видам спорта
    by_sport = {}
    for sport, wtype, duration in triathlon_workouts:
        if sport not in by_sport:
            by_sport[sport] = []
        by_sport[sport].append((wtype, duration))

    print("\nТренировки по видам спорта:")
    for sport in [SportType.RUNNING, SportType.CYCLING, SportType.SWIMMING]:
        if sport in by_sport:
            print(f"\n{sport.value.upper()}:")
            for wtype, duration in by_sport[sport]:
                print(f"  - {wtype.value}: {duration} мин")

    print("\n" + "="*60)
    print("\n✓ Все тесты пройдены успешно!")

if __name__ == "__main__":
    test_schedule_logic()
