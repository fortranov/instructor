"""
Модуль для мастера создания планов тренировок
Содержит логику расчета сложности плана на основе ответов пользователя
"""

from database import CompetitionType, WorkoutCoefficients, SessionLocal
from datetime import date

# Коэффициенты для расчета сложности плана
# Эти значения можно легко редактировать для настройки алгоритма

# Коэффициенты для недельного километража
WEEKLY_DISTANCE_COEFFICIENTS = {
    'beginner': 10,      # Только начинаю бегать
    '5-10': 50,         # 5-10 км
    '10-30': 100,        # 10-30 км  
    '30-50': 200,        # 30-50 км
    '50+': 300,          # Больше 50 км
}

# Коэффициенты для комфортного темпа
PACE_COEFFICIENTS = {
    '8+': 20,            # Медленнее 8 мин/км
    '7-8': 50,          # 7-8 мин/км
    '6-7': 100,          # 6-7 мин/км
    '5-6': 150,          # 5-6 мин/км
    '4-5': 200,          # 4-5 мин/км
    '4-': 300,           # Быстрее 4 мин/км
}

# Коэффициенты для целевой дистанции
TARGET_DISTANCE_COEFFICIENTS = {
    '5k': 50,            # 5 км
    '10k': 100,          # 10 км
    '21k': 150,          # 21 км (полумарафон)
    '42k': 250,          # 42 км (марафон)
}

# Коэффициент для времени подготовки (чем меньше времени, тем выше сложность)
TIME_PREPARATION_BASE = 100
TIME_PREPARATION_WEEKS_OPTIMAL = 16  # Оптимальное количество недель для подготовки

def get_coefficients_from_db():
    """Получить коэффициенты из базы данных"""
    db = SessionLocal()
    try:
        coefficients = db.query(WorkoutCoefficients).first()
        if not coefficients:
            # Если коэффициентов нет в БД, используем значения по умолчанию
            return {
                'weekly_distance': WEEKLY_DISTANCE_COEFFICIENTS,
                'pace': PACE_COEFFICIENTS,
                'target_distance': TARGET_DISTANCE_COEFFICIENTS,
                'time_preparation_base': TIME_PREPARATION_BASE,
                'time_preparation_weeks_optimal': TIME_PREPARATION_WEEKS_OPTIMAL
            }
        
        return {
            'weekly_distance': {
                'beginner': coefficients.weekly_distance_beginner,
                '5-10': coefficients.weekly_distance_5_10,
                '10-30': coefficients.weekly_distance_10_30,
                '30-50': coefficients.weekly_distance_30_50,
                '50+': coefficients.weekly_distance_50_plus,
            },
            'pace': {
                '8+': coefficients.pace_8_plus,
                '7-8': coefficients.pace_7_8,
                '6-7': coefficients.pace_6_7,
                '5-6': coefficients.pace_5_6,
                '4-5': coefficients.pace_4_5,
                '4-': coefficients.pace_4_minus,
            },
            'target_distance': {
                '5k': coefficients.target_distance_5k,
                '10k': coefficients.target_distance_10k,
                '21k': coefficients.target_distance_21k,
                '42k': coefficients.target_distance_42k,
            },
            'time_preparation_base': coefficients.time_preparation_base,
            'time_preparation_weeks_optimal': coefficients.time_preparation_weeks_optimal
        }
    finally:
        db.close()

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
    
    # Получаем коэффициенты из базы данных
    coeffs = get_coefficients_from_db()
    
    complexity = 0
    
    # Базовая сложность на основе недельного километража
    complexity += coeffs['weekly_distance'].get(weekly_distance, 200)
    
    # Добавляем сложность на основе темпа
    complexity += coeffs['pace'].get(comfortable_pace, 100)
    
    # Добавляем сложность на основе целевой дистанции
    complexity += coeffs['target_distance'].get(target_distance, 100)
    
    # Корректировка на основе времени подготовки
    if has_specific_goal:
        from datetime import datetime
        today = datetime.now().date()
        weeks_to_competition = (competition_date - today).days // 7
        
        if weeks_to_competition < coeffs['time_preparation_weeks_optimal']:
            # Если времени мало, увеличиваем сложность
            time_factor = coeffs['time_preparation_base'] * (coeffs['time_preparation_weeks_optimal'] / max(weeks_to_competition, 1))
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
