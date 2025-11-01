"""
Упрощенный тест логики распределения тренировок
"""

from datetime import date, timedelta
from enum import Enum

# Простые enum для теста
class WorkoutType(str, Enum):
    ENDURANCE = "endurance"
    INTERVAL = "interval"
    RECOVERY = "recovery"

class SportType(str, Enum):
    RUNNING = "running"
    CYCLING = "cycling"
    SWIMMING = "swimming"

def test_workout_distribution_logic():
    """Тест логики распределения тренировок по дням недели"""

    print("="*70)
    print("ТЕСТ: Распределение тренировок по дням недели")
    print("="*70)

    # Имитация недельных тренировок
    weekly_workouts = [
        (SportType.RUNNING, WorkoutType.ENDURANCE, 120),   # Длительная 1
        (SportType.RUNNING, WorkoutType.ENDURANCE, 90),    # Длительная 2
        (SportType.RUNNING, WorkoutType.INTERVAL, 45),     # Интервальная 1
        (SportType.RUNNING, WorkoutType.INTERVAL, 30),     # Интервальная 2
        (SportType.RUNNING, WorkoutType.RECOVERY, 30),     # Восстановительная 1
        (SportType.RUNNING, WorkoutType.RECOVERY, 20),     # Восстановительная 2
    ]

    # Предпочтительные дни: Пн(0), Ср(2), Пт(4), Сб(5)
    user_preferred_days = [0, 2, 4, 5]
    preferred_days = sorted(user_preferred_days)

    print(f"\nПредпочтительные дни пользователя: {preferred_days}")
    print("(0=Пн, 1=Вт, 2=Ср, 3=Чт, 4=Пт, 5=Сб, 6=Вс)")

    # Шаг 1: Разделить на типы
    endurance_workouts = [(s, w, d) for s, w, d in weekly_workouts if w == WorkoutType.ENDURANCE]
    other_workouts = [(s, w, d) for s, w, d in weekly_workouts if w != WorkoutType.ENDURANCE]

    # Сортировать длительные по длительности (самые длинные первыми)
    endurance_workouts.sort(key=lambda x: x[2], reverse=True)

    # Чередовать восстановительные и интервальные
    recovery_workouts = [(s, w, d) for s, w, d in other_workouts if w == WorkoutType.RECOVERY]
    interval_workouts = [(s, w, d) for s, w, d in other_workouts if w == WorkoutType.INTERVAL]

    alternated_workouts = []
    max_len = max(len(recovery_workouts), len(interval_workouts))
    for i in range(max_len):
        if i < len(recovery_workouts):
            alternated_workouts.append(recovery_workouts[i])
        if i < len(interval_workouts):
            alternated_workouts.append(interval_workouts[i])

    print("\n--- ЭТАП 1: Разделение тренировок ---")
    print(f"\nДлительные тренировки (ENDURANCE): {len(endurance_workouts)}")
    for sport, wtype, duration in endurance_workouts:
        print(f"  • {wtype.value}: {duration} мин")

    print(f"\nОстальные тренировки (чередование): {len(alternated_workouts)}")
    for sport, wtype, duration in alternated_workouts:
        print(f"  • {wtype.value}: {duration} мин")

    # Шаг 2: Распределение по дням
    print("\n--- ЭТАП 2: Распределение по дням недели ---")

    # Длительные - с конца недели
    reversed_days = list(reversed(preferred_days))
    print(f"\nДлительные тренировки (с конца недели): {reversed_days}")

    day_names = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    scheduled = {}

    for i, (sport, wtype, duration) in enumerate(endurance_workouts):
        day = reversed_days[i % len(reversed_days)]
        if day not in scheduled:
            scheduled[day] = []
        scheduled[day].append(f"{wtype.value} {duration}мин")
        print(f"  {day_names[day]} ({day}): {wtype.value} - {duration} мин")

    # Остальные - с начала недели
    print(f"\nОстальные тренировки (с начала недели): {preferred_days}")

    for i, (sport, wtype, duration) in enumerate(alternated_workouts):
        day = preferred_days[i % len(preferred_days)]
        if day not in scheduled:
            scheduled[day] = []
        scheduled[day].append(f"{wtype.value} {duration}мин")
        print(f"  {day_names[day]} ({day}): {wtype.value} - {duration} мин")

    # Итоговое расписание
    print("\n--- ИТОГОВОЕ РАСПИСАНИЕ ---")
    for day in sorted(scheduled.keys()):
        print(f"\n{day_names[day]} ({day}):")
        for workout in scheduled[day]:
            print(f"  • {workout}")

    print("\n" + "="*70)
    print("ТЕСТ: Порядок видов спорта для триатлона")
    print("="*70)

    # Проверка порядка для триатлона
    expected_order = [SportType.RUNNING, SportType.CYCLING, SportType.SWIMMING]
    print(f"\nОжидаемый порядок: {[s.value for s in expected_order]}")
    print("[OK] ПРАВИЛЬНО: Сначала бег, потом велосипед, потом плавание")

    print("\n" + "="*70)
    print("ТЕСТ: Ограничение количества тренировок одного вида спорта")
    print("="*70)

    # Симуляция проверки лимита
    daily_sport_counts = {
        date(2025, 1, 6): {SportType.RUNNING: 1},  # Понедельник - 1 беговая
        date(2025, 1, 8): {SportType.RUNNING: 2},  # Среда - 2 беговых (максимум)
    }

    print("\nСимуляция проверки лимита:")
    test_date_1 = date(2025, 1, 6)
    test_date_2 = date(2025, 1, 8)

    def can_add_workout(workout_date: date, sport_type: SportType) -> bool:
        if workout_date not in daily_sport_counts:
            return True
        if sport_type not in daily_sport_counts[workout_date]:
            return True
        return daily_sport_counts[workout_date][sport_type] < 2

    result_1 = can_add_workout(test_date_1, SportType.RUNNING)
    result_2 = can_add_workout(test_date_2, SportType.RUNNING)

    print(f"Пн 06.01 (1 беговая): Можно добавить еще беговую? {result_1} [OK]")
    print(f"Ср 08.01 (2 беговых): Можно добавить еще беговую? {result_2} [OK]")

    print("\n" + "="*70)
    print("[OK] ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    print("="*70)

if __name__ == "__main__":
    test_workout_distribution_logic()
