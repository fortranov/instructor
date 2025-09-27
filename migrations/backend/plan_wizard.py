"""
Модуль для мастера создания планов тренировок
Содержит логику расчета сложности плана на основе ответов пользователя
"""

from database import CompetitionType
from datetime import date

# Коэффициенты для расчета сложности плана
# Эти значения можно легко редактировать для настройки алгоритма

# Коэффициенты для недельного километража
WEEKLY_DISTANCE_COEFFICIENTS = {
    'beginner': 100,      # Только начинаю бегать
    '5-10': 200,         # 5-10 км
    '10-30': 400,        # 10-30 км  
    '30-50': 600,        # 30-50 км
    '50+': 800,          # Больше 50 км
}

# Коэффициенты для комфортного темпа
PACE_COEFFICIENTS = {
    '8+': 50,            # Медленнее 8 мин/км
    '7-8': 100,          # 7-8 мин/км
    '6-7': 200,          # 6-7 мин/км
    '5-6': 350,          # 5-6 мин/км
    '4-5': 500,          # 4-5 мин/км
    '4-': 650,           # Быстрее 4 мин/км
}

# Коэффициенты для целевой дистанции
TARGET_DISTANCE_COEFFICIENTS = {
    '5k': 50,            # 5 км
    '10k': 100,          # 10 км
    '21k': 200,          # 21 км (полумарафон)
    '42k': 350,          # 42 км (марафон)
}

# Коэффициент для времени подготовки (чем меньше времени, тем выше сложность)
TIME_PREPARATION_BASE = 100
TIME_PREPARATION_WEEKS_OPTIMAL = 16  # Оптимальное количество недель для подготовки

def calculate_plan_complexity(
    weekly_distance: str,
    comfortable_pace: str,
    target_distance: str,
    competition_date: date,
    has_specific_goal: bool
) -> int:
    """
    Рассчитывает сложность плана на основе ответов пользователя
    
    Args:
        weekly_distance: Недельный километраж
        comfortable_pace: Комфортный темп бега
        target_distance: Целевая дистанция
        competition_date: Дата соревнования
        has_specific_goal: Есть ли конкретная цель
        
    Returns:
        int: Сложность плана от 0 до 1000
    """
    
    complexity = 0
    
    # Базовая сложность на основе недельного километража
    complexity += WEEKLY_DISTANCE_COEFFICIENTS.get(weekly_distance, 200)
    
    # Добавляем сложность на основе темпа
    complexity += PACE_COEFFICIENTS.get(comfortable_pace, 100)
    
    # Добавляем сложность на основе целевой дистанции
    complexity += TARGET_DISTANCE_COEFFICIENTS.get(target_distance, 100)
    
    # Корректировка на основе времени подготовки
    if has_specific_goal:
        from datetime import datetime
        today = datetime.now().date()
        weeks_to_competition = (competition_date - today).days // 7
        
        if weeks_to_competition < TIME_PREPARATION_WEEKS_OPTIMAL:
            # Если времени мало, увеличиваем сложность
            time_factor = TIME_PREPARATION_BASE * (TIME_PREPARATION_WEEKS_OPTIMAL / max(weeks_to_competition, 1))
            complexity += min(time_factor, 200)  # Ограничиваем максимальную добавку
        else:
            # Если времени достаточно, немного снижаем сложность
            complexity -= 50
    else:
        # Если нет конкретной цели, используем среднюю сложность
        complexity += 50
    
    # Ограничиваем сложность в диапазоне 0-1000
    complexity = max(0, min(1000, int(complexity)))
    
    return complexity

def determine_competition_type(target_distance: str) -> CompetitionType:
    """
    Определяет тип соревнования на основе целевой дистанции
    
    Args:
        target_distance: Целевая дистанция
        
    Returns:
        CompetitionType: Тип соревнования
    """
    
    distance_mapping = {
        '5k': CompetitionType.RUN_10K,  # Используем 10K как ближайший
        '10k': CompetitionType.RUN_10K,
        '21k': CompetitionType.RUN_HALF_MARATHON,
        '42k': CompetitionType.RUN_MARATHON,
    }
    
    return distance_mapping.get(target_distance, CompetitionType.RUN_10K)
