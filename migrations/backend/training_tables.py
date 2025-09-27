"""
Таблицы тренировок по методике Джо Фрила
Основаны на принципах периодизации и структурированного подхода к тренировкам
"""

from typing import Dict, List, Tuple
from database import SportType, WorkoutType, CompetitionType
from datetime import date, timedelta

class TrainingTables:
    """Класс для работы с таблицами тренировок по методике Джо Фрила"""
    
    # Базовые объемы тренировок в минутах в зависимости от сложности (0-1000)
    BASE_WEEKLY_VOLUMES = {
        SportType.RUNNING: {
            0: 120,      # 2 часа в неделю для начинающих
            250: 180,    # 3 часа
            500: 300,    # 5 часов
            750: 420,    # 7 часов
            1000: 600    # 10 часов для продвинутых
        },
        SportType.CYCLING: {
            0: 180,      # 3 часа в неделю
            250: 300,    # 5 часов
            500: 480,    # 8 часов
            750: 720,    # 12 часов
            1000: 1080   # 18 часов
        },
        SportType.SWIMMING: {
            0: 90,       # 1.5 часа в неделю
            250: 120,    # 2 часа
            500: 180,    # 3 часа
            750: 240,    # 4 часа
            1000: 360    # 6 часов
        }
    }
    
    # Распределение типов тренировок по фазам подготовки (в процентах)
    WORKOUT_DISTRIBUTION = {
        'base': {  # Базовая фаза (8-12 недель до соревнования)
            WorkoutType.ENDURANCE: 0.7,    # 70% длительные
            WorkoutType.RECOVERY: 0.25,     # 25% восстанавливающие
            WorkoutType.INTERVAL: 0.05      # 5% интервальные
        },
        'build': {  # Развивающая фаза (4-8 недель до соревнования)
            WorkoutType.ENDURANCE: 0.5,     # 50% длительные
            WorkoutType.INTERVAL: 0.35,     # 35% интервальные
            WorkoutType.RECOVERY: 0.15      # 15% восстанавливающие
        },
        'peak': {  # Пиковая фаза (2-4 недели до соревнования)
            WorkoutType.INTERVAL: 0.5,      # 50% интервальные
            WorkoutType.ENDURANCE: 0.3,     # 30% длительные
            WorkoutType.RECOVERY: 0.2       # 20% восстанавливающие
        },
        'taper': {  # Снижение нагрузки (1-2 недели до соревнования)
            WorkoutType.RECOVERY: 0.6,      # 60% восстанавливающие
            WorkoutType.INTERVAL: 0.25,     # 25% интервальные
            WorkoutType.ENDURANCE: 0.15     # 15% длительные
        }
    }
    
    # Продолжительность отдельных тренировок по типам (в минутах)
    WORKOUT_DURATIONS = {
        WorkoutType.ENDURANCE: {
            SportType.RUNNING: (45, 120),    # от 45 до 120 минут
            SportType.CYCLING: (60, 180),    # от 60 до 180 минут
            SportType.SWIMMING: (30, 90)     # от 30 до 90 минут
        },
        WorkoutType.INTERVAL: {
            SportType.RUNNING: (30, 60),     # от 30 до 60 минут
            SportType.CYCLING: (45, 90),     # от 45 до 90 минут
            SportType.SWIMMING: (30, 60)     # от 30 до 60 минут
        },
        WorkoutType.RECOVERY: {
            SportType.RUNNING: (20, 45),     # от 20 до 45 минут
            SportType.CYCLING: (30, 60),     # от 30 до 60 минут
            SportType.SWIMMING: (20, 40)     # от 20 до 40 минут
        }
    }
    
    # Количество тренировок в неделю для разных видов спорта
    WEEKLY_FREQUENCY = {
        SportType.RUNNING: (3, 6),       # от 3 до 6 тренировок в неделю
        SportType.CYCLING: (3, 5),       # от 3 до 5 тренировок в неделю
        SportType.SWIMMING: (3, 6)       # от 3 до 6 тренировок в неделю
    }
    
    @staticmethod
    def get_weekly_volume(sport_type: SportType, complexity: int) -> int:
        """Получить недельный объем тренировок в минутах"""
        volumes = TrainingTables.BASE_WEEKLY_VOLUMES[sport_type]
        
        # Интерполяция между ближайшими значениями
        complexity_levels = sorted(volumes.keys())
        
        if complexity <= complexity_levels[0]:
            return volumes[complexity_levels[0]]
        elif complexity >= complexity_levels[-1]:
            return volumes[complexity_levels[-1]]
        
        # Найти ближайшие уровни сложности
        for i in range(len(complexity_levels) - 1):
            if complexity_levels[i] <= complexity <= complexity_levels[i + 1]:
                lower = complexity_levels[i]
                upper = complexity_levels[i + 1]
                
                # Линейная интерполяция
                ratio = (complexity - lower) / (upper - lower)
                volume = volumes[lower] + (volumes[upper] - volumes[lower]) * ratio
                return int(volume)
        
        return volumes[500]  # Значение по умолчанию
    
    @staticmethod
    def get_training_phase(weeks_to_competition: int) -> str:
        """Определить фазу тренировки в зависимости от времени до соревнования"""
        if weeks_to_competition <= 2:
            return 'taper'
        elif weeks_to_competition <= 4:
            return 'peak'
        elif weeks_to_competition <= 8:
            return 'build'
        else:
            return 'base'
    
    @staticmethod
    def get_sport_types_for_competition(competition_type: CompetitionType) -> List[SportType]:
        """Получить типы спорта для конкретного типа соревнования"""
        if competition_type in [CompetitionType.RUN_10K, CompetitionType.RUN_HALF_MARATHON, CompetitionType.RUN_MARATHON]:
            return [SportType.RUNNING]
        elif competition_type == CompetitionType.CYCLING:
            return [SportType.CYCLING]
        elif competition_type == CompetitionType.SWIMMING:
            return [SportType.SWIMMING]
        elif competition_type in [CompetitionType.TRIATHLON_SPRINT, CompetitionType.TRIATHLON_OLYMPIC, CompetitionType.TRIATHLON_IRONMAN]:
            return [SportType.SWIMMING, SportType.CYCLING, SportType.RUNNING]
        
        return [SportType.RUNNING]  # По умолчанию
    
    @staticmethod
    def get_weekly_frequency(sport_type: SportType, complexity: int) -> int:
        """Получить количество тренировок в неделю"""
        min_freq, max_freq = TrainingTables.WEEKLY_FREQUENCY[sport_type]
        
        # Частота зависит от сложности
        frequency = min_freq + (max_freq - min_freq) * (complexity / 1000)
        return max(min_freq, min(max_freq, int(round(frequency))))
    
    @staticmethod
    def get_workout_duration(workout_type: WorkoutType, sport_type: SportType, complexity: int) -> int:
        """Получить продолжительность тренировки"""
        min_duration, max_duration = TrainingTables.WORKOUT_DURATIONS[workout_type][sport_type]
        
        # Продолжительность зависит от сложности
        duration = min_duration + (max_duration - min_duration) * (complexity / 1000)
        return int(round(duration))
    
    @staticmethod
    def distribute_weekly_workouts(sport_types: List[SportType], weekly_volume: int, 
                                 phase: str, complexity: int) -> List[Tuple[SportType, WorkoutType, int]]:
        """Распределить недельные тренировки по типам спорта и типам тренировок"""
        workouts = []
        distribution = TrainingTables.WORKOUT_DISTRIBUTION[phase]
        
        # Если один вид спорта
        if len(sport_types) == 1:
            sport_type = sport_types[0]
            frequency = TrainingTables.get_weekly_frequency(sport_type, complexity)
            
            # Рассчитать общее количество тренировок для распределения объема
            total_workouts = 0
            workout_counts = {}
            for workout_type, ratio in distribution.items():
                count = max(1, int(frequency * ratio))
                workout_counts[workout_type] = count
                total_workouts += count
            
            # Распределить недельный объем между тренировками
            for workout_type, ratio in distribution.items():
                count = workout_counts[workout_type]
                # Рассчитать объем для этого типа тренировок
                type_volume = int(weekly_volume * ratio)
                # Разделить объем между тренировками этого типа
                duration = max(20, type_volume // count) if count > 0 else 60  # Минимум 20 минут
                
                for _ in range(count):
                    workouts.append((sport_type, workout_type, duration))
        
        # Если триатлон (три вида спорта)
        else:
            volume_per_sport = weekly_volume // len(sport_types)
            
            for sport_type in sport_types:
                frequency = TrainingTables.get_weekly_frequency(sport_type, complexity)
                frequency = max(2, frequency // 2)  # Меньше тренировок каждого вида для триатлона
                
                # Рассчитать общее количество тренировок для этого вида спорта
                total_workouts = 0
                workout_counts = {}
                for workout_type, ratio in distribution.items():
                    count = max(1, int(frequency * ratio))
                    workout_counts[workout_type] = count
                    total_workouts += count
                
                # Распределить объем для этого вида спорта
                for workout_type, ratio in distribution.items():
                    count = workout_counts[workout_type]
                    # Рассчитать объем для этого типа тренировок
                    type_volume = int(volume_per_sport * ratio)
                    # Разделить объем между тренировками этого типа
                    duration = max(20, type_volume // count) if count > 0 else 45  # Минимум 20 минут
                    
                    for _ in range(count):
                        workouts.append((sport_type, workout_type, duration))
        
        return workouts
