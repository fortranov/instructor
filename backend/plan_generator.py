"""
Генератор персонализированных планов тренировок
"""

from typing import List, Dict
from datetime import date, timedelta
from sqlalchemy.orm import Session
import random

from database import User, TrainingPlan, Workout, CompetitionType, WorkoutCompletionMark, WorkoutType, SportType
from training_tables import TrainingTables
from schemas import TrainingPlanCreate

class PlanGenerator:
    """Класс для генерации персонализированных планов тренировок"""
    
    def __init__(self, db: Session):
        self.db = db
        self.training_tables = TrainingTables()
    
    def create_training_plan(self, plan_data: TrainingPlanCreate) -> TrainingPlan:
        """Создать персонализированный план тренировок"""
        
        # Найти пользователя
        user = self.db.query(User).filter(User.uin == plan_data.uin).first()
        if not user:
            # Если пользователь не найден, это ошибка - пользователь должен существовать
            raise ValueError(f"Пользователь с UIN {plan_data.uin} не найден. Создание плана невозможно.")
        
        # Убедиться, что у пользователя есть предпочтительные дни
        if not user.preferred_workout_days:
            import json
            user.preferred_workout_days = json.dumps([0, 1, 2, 3, 4, 5, 6])  # Дни недели по умолчанию (все дни)
            self.db.flush()
        
        # Удалить существующий план пользователя, если есть
        existing_plan = self.db.query(TrainingPlan).filter(TrainingPlan.user_id == user.id).first()
        if existing_plan:
            self.db.delete(existing_plan)
            self.db.flush()
        
        # Создать новый план
        new_plan = TrainingPlan(
            user_id=user.id,
            complexity=plan_data.complexity,
            competition_date=plan_data.competition_date,
            competition_type=plan_data.competition_type,
            competition_distance=plan_data.competition_distance
        )
        
        self.db.add(new_plan)
        self.db.flush()  # Получить ID плана
        
        # Генерировать тренировки (уже отфильтрованные)
        workouts = self._generate_workouts(new_plan)
        
        # Добавить тренировки в базу данных
        for workout_data in workouts:
            workout = Workout(
                plan_id=new_plan.id,
                date=workout_data['date'],
                sport_type=workout_data['sport_type'],
                duration_minutes=workout_data['duration_minutes'],
                workout_type=workout_data['workout_type']
            )
            self.db.add(workout)
        
        self.db.commit()
        self.db.refresh(new_plan)
        
        return new_plan
    
    def _generate_workouts(self, plan: TrainingPlan) -> List[Dict]:
        """Генерировать тренировки для плана"""
        workouts = []

        # Получить предпочтительные дни пользователя
        user_preferred_days = self._get_user_preferred_days(plan.user_id)

        # Получить информацию о силовых тренировках
        user = self.db.query(User).filter(User.id == plan.user_id).first()
        has_strength_training = bool(user.has_strength_training) if user else False

        # Определить виды спорта для типа соревнования
        sport_types = self.training_tables.get_sport_types_for_competition(plan.competition_type)
        
        # Рассчитать количество недель до соревнования
        today = date.today()
        days_to_competition = (plan.competition_date - today).days
        weeks_to_competition = max(1, days_to_competition // 7)
        
        # Генерировать тренировки по неделям
        # Начать с понедельника текущей недели
        days_since_monday = today.weekday()  # 0 = понедельник, 6 = воскресенье
        current_date = today - timedelta(days=days_since_monday)
        week_count = 0
        
        while current_date < plan.competition_date:
            week_count += 1
            weeks_remaining = max(1, (plan.competition_date - current_date).days // 7)
            
            
            # Определить фазу тренировки
            phase = self.training_tables.get_training_phase(weeks_remaining)
            
            # Получить недельный объем для основного вида спорта
            primary_sport = sport_types[0]
            weekly_volume = self.training_tables.get_weekly_volume(primary_sport, plan.complexity)
            
            # Скорректировать объем в зависимости от фазы и недельной периодизации
            volume_multiplier = self._get_volume_multiplier(phase, weeks_remaining, week_count)
            adjusted_volume = int(weekly_volume * volume_multiplier)
            
            # Распределить тренировки на неделю
            weekly_workouts = self.training_tables.distribute_weekly_workouts(
                sport_types, adjusted_volume, phase, plan.complexity
            )
            
            # Назначить даты тренировкам в течение недели
            week_workouts = self._schedule_weekly_workouts(
                weekly_workouts, current_date, plan.competition_date, user_preferred_days
            )

            workouts.extend(week_workouts)

            # Добавить силовую тренировку в фазах base, build и peak, если пользователь указал возможность
            # Не добавляем силовые только в фазе taper (за 2 недели до соревнования)
            if has_strength_training and phase in ['base', 'build', 'peak']:
                strength_workout = self._add_strength_workout(
                    current_date, plan.competition_date, user_preferred_days, week_workouts
                )
                if strength_workout:
                    workouts.append(strength_workout)

            # Перейти к следующей неделе (к понедельнику)
            days_since_monday = current_date.weekday()  # 0 = понедельник, 6 = воскресенье
            current_date = current_date + timedelta(days=7 - days_since_monday)
        
        # Тренировки уже созданы с учетом предпочтительных дней в _schedule_weekly_workouts
        return workouts
    
    def _filter_workouts_by_preferred_days(self, workouts: List[Dict], user_id: int) -> List[Dict]:
        """Фильтровать тренировки по предпочтительным дням пользователя"""
        # Получить предпочтительные дни пользователя
        preferred_days = self._get_user_preferred_days(user_id)
        
        filtered_workouts = []
        
        for workout in workouts:
            # Получить день недели тренировки
            workout_date = workout['date']
            if isinstance(workout_date, str):
                workout_date = date.fromisoformat(workout_date)
            
            day_of_week = workout_date.weekday()  # 0 = понедельник, 6 = воскресенье
            
            # Проверить, соответствует ли день предпочтительным дням
            if day_of_week in preferred_days:
                filtered_workouts.append(workout)
            # Если день не в предпочтительных днях, тренировка исключается (не переносится)
        
        return filtered_workouts
    
    def _move_workout_to_preferred_day(self, workout: Dict, preferred_days: List[int]) -> Dict:
        """Перенести тренировку на ближайший предпочтительный день"""
        workout_date = workout['date']
        if isinstance(workout_date, str):
            workout_date = date.fromisoformat(workout_date)
        
        current_day = workout_date.weekday()
        
        # Найти ближайший предпочтительный день
        min_distance = float('inf')
        best_day = None
        
        for preferred_day in preferred_days:
            # Рассчитать расстояние до предпочтительного дня
            distance = (preferred_day - current_day) % 7
            if distance == 0:
                distance = 7  # Если это тот же день, перенести на следующую неделю
            
            if distance < min_distance:
                min_distance = distance
                best_day = preferred_day
        
        if best_day is not None:
            # Перенести тренировку на найденный день
            new_date = workout_date + timedelta(days=min_distance)
            moved_workout = workout.copy()
            moved_workout['date'] = new_date
            return moved_workout
        
        return None
    
    def _filter_workouts_by_preferred_days_from_db(self, workouts: List, user_id: int) -> List:
        """Фильтровать тренировки из базы данных по предпочтительным дням пользователя"""
        # Получить предпочтительные дни пользователя
        preferred_days = self._get_user_preferred_days(user_id)
        
        filtered_workouts = []
        for workout in workouts:
            # Получить день недели тренировки
            workout_date = workout.date
            if isinstance(workout_date, str):
                workout_date = date.fromisoformat(workout_date)
            
            day_of_week = workout_date.weekday()  # 0 = понедельник, 6 = воскресенье
            
            # Проверить, соответствует ли день предпочтительным дням
            if day_of_week in preferred_days:
                filtered_workouts.append(workout)
        
        return filtered_workouts
    
    def _get_volume_multiplier(self, phase: str, weeks_remaining: int, week_number: int = None) -> float:
        """
        Получить множитель объема тренировок в зависимости от фазы и недельной периодизации
        
        Реализует 4-недельную периодизацию объема тренировок:
        - Неделя 1: базовый объем (1.0)
        - Неделя 2: +25% объема (1.25) 
        - Неделя 3: +37% объема (1.37)
        - Неделя 4: -25% объема (0.75) - разгрузочная неделя
        
        Args:
            phase: Фаза тренировки ('base', 'build', 'peak', 'taper')
            weeks_remaining: Количество недель до соревнования
            week_number: Номер недели в плане (для периодизации)
            
        Returns:
            float: Множитель для корректировки базового объема тренировок
        """
        multipliers = {
            'base': 1.0,      # Полный объем в базовой фазе
            'build': 1.1,     # Увеличенный объем в развивающей фазе
            'peak': 0.9,      # Немного сниженный объем в пиковой фазе
            'taper': 0.6      # Значительно сниженный объем перед соревнованием
        }
        
        base_multiplier = multipliers.get(phase, 1.0)
        
        # Дополнительная корректировка в зависимости от недель до соревнования
        if weeks_remaining == 1:
            return base_multiplier * 0.5  # Очень легкая неделя перед соревнованием
        elif weeks_remaining == 2:
            return base_multiplier * 0.7  # Легкая неделя
        
        # 4-недельная периодизация объема тренировок
        if week_number is not None:
            week_in_cycle = (week_number - 1) % 4 + 1  # Определяем неделю в 4-недельном цикле (1-4)
            
            # Коэффициенты для каждой недели цикла
            cycle_multipliers = {
                1: 1.0,     # Неделя 1 - базовый объем
                2: 1.25,    # Неделя 2 - +25% объема
                3: 1.37,    # Неделя 3 - +37% объема  
                4: 0.75     # Неделя 4 - -25% объема (разгрузочная)
            }
            
            cycle_multiplier = cycle_multipliers.get(week_in_cycle, 1.0)
            return base_multiplier * cycle_multiplier
        
        return base_multiplier
    
    def _get_user_preferred_days(self, user_id: int) -> List[int]:
        """Получить предпочтительные дни для тренировок пользователя"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user or not user.preferred_workout_days:
            return [0, 1, 2, 3, 4, 5, 6]  # Дни недели по умолчанию (все дни)
        
        try:
            import json
            preferred_days = json.loads(user.preferred_workout_days)
            return preferred_days
        except (json.JSONDecodeError, TypeError):
            return [0, 1, 2, 3, 4, 5, 6]  # Fallback к значению по умолчанию (все дни)
    
    def _schedule_weekly_workouts(self, weekly_workouts: List, start_date: date,
                                competition_date: date, user_preferred_days: List[int] = None) -> List[Dict]:
        """
        Распределить тренировки по дням недели с учетом типа тренировок и вида спорта.

        Алгоритм:
        1. Длительные тренировки (ENDURANCE) размещаются с конца недели (последние предпочтительные дни)
        2. Остальные тренировки (RECOVERY и INTERVAL) размещаются с начала недели, чередуясь
        3. В день не может быть более 2 тренировок одного вида спорта
        """
        scheduled_workouts = []

        # Предпочтительные дни для тренировок (понедельник = 0, воскресенье = 6)
        if user_preferred_days is not None and len(user_preferred_days) > 0:
            preferred_days = sorted(user_preferred_days)  # Сортируем для корректного распределения
        else:
            preferred_days = [0, 1, 2, 3, 4, 5, 6]  # Дни недели по умолчанию (все дни)

        # Разделить тренировки на длительные и остальные
        endurance_workouts = []
        other_workouts = []

        for sport_type, workout_type, duration in weekly_workouts:
            if workout_type == WorkoutType.ENDURANCE:
                endurance_workouts.append((sport_type, workout_type, duration))
            else:
                other_workouts.append((sport_type, workout_type, duration))

        # Сортировать длительные тренировки по длительности (самые длинные первыми)
        endurance_workouts.sort(key=lambda x: x[2], reverse=True)

        # Чередовать восстановительные и интервальные тренировки
        recovery_workouts = [(s, w, d) for s, w, d in other_workouts if w == WorkoutType.RECOVERY]
        interval_workouts = [(s, w, d) for s, w, d in other_workouts if w == WorkoutType.INTERVAL]

        alternated_workouts = []
        max_len = max(len(recovery_workouts), len(interval_workouts))
        for i in range(max_len):
            if i < len(recovery_workouts):
                alternated_workouts.append(recovery_workouts[i])
            if i < len(interval_workouts):
                alternated_workouts.append(interval_workouts[i])

        # Рассчитать понедельник текущей недели
        days_since_monday = start_date.weekday()  # 0 = понедельник, 6 = воскресенье
        monday_of_week = start_date - timedelta(days=days_since_monday)

        # Словарь для отслеживания количества тренировок каждого вида спорта по дням
        # Формат: {дата: {SportType: количество}}
        daily_sport_counts = {}

        def can_add_workout(workout_date: date, sport_type: SportType) -> bool:
            """Проверить, можно ли добавить тренировку данного вида спорта в этот день"""
            if workout_date not in daily_sport_counts:
                return True
            if sport_type not in daily_sport_counts[workout_date]:
                return True
            # Максимум 2 тренировки одного вида спорта в день
            return daily_sport_counts[workout_date][sport_type] < 2

        def add_workout(workout_date: date, sport_type: SportType, workout_type: WorkoutType, duration: int):
            """Добавить тренировку и обновить счетчик"""
            if workout_date not in daily_sport_counts:
                daily_sport_counts[workout_date] = {}
            if sport_type not in daily_sport_counts[workout_date]:
                daily_sport_counts[workout_date][sport_type] = 0
            daily_sport_counts[workout_date][sport_type] += 1

            scheduled_workouts.append({
                'date': workout_date,
                'sport_type': sport_type,
                'duration_minutes': duration,
                'workout_type': workout_type
            })

        # 1. Распределить длительные тренировки с конца недели (последние предпочтительные дни)
        reversed_days = list(reversed(preferred_days))
        day_index = 0

        for sport_type, workout_type, duration in endurance_workouts:
            placed = False
            attempts = 0
            max_attempts = len(preferred_days) * 3  # Максимум попыток для избежания бесконечного цикла

            while not placed and attempts < max_attempts:
                preferred_day = reversed_days[day_index % len(reversed_days)]
                workout_date = monday_of_week + timedelta(days=preferred_day)

                # Если дата в прошлом, перенести на следующую неделю
                if workout_date < start_date:
                    workout_date = workout_date + timedelta(days=7)

                # Проверить, что дата не превышает дату соревнования
                if workout_date >= competition_date:
                    day_index += 1
                    attempts += 1
                    continue

                # Проверить лимит тренировок данного вида спорта в этот день
                if can_add_workout(workout_date, sport_type):
                    add_workout(workout_date, sport_type, workout_type, duration)
                    placed = True

                day_index += 1
                attempts += 1

        # 2. Распределить остальные тренировки с начала недели, чередуя восстановительные и интервальные
        day_index = 0

        for sport_type, workout_type, duration in alternated_workouts:
            placed = False
            attempts = 0
            max_attempts = len(preferred_days) * 3

            while not placed and attempts < max_attempts:
                preferred_day = preferred_days[day_index % len(preferred_days)]
                workout_date = monday_of_week + timedelta(days=preferred_day)

                # Если дата в прошлом, перенести на следующую неделю
                if workout_date < start_date:
                    workout_date = workout_date + timedelta(days=7)

                # Проверить, что дата не превышает дату соревнования
                if workout_date >= competition_date:
                    day_index += 1
                    attempts += 1
                    continue

                # Проверить лимит тренировок данного вида спорта в этот день
                if can_add_workout(workout_date, sport_type):
                    add_workout(workout_date, sport_type, workout_type, duration)
                    placed = True

                day_index += 1
                attempts += 1

        return scheduled_workouts

    def _add_strength_workout(self, start_date: date, competition_date: date,
                              user_preferred_days: List[int], week_workouts: List[Dict]) -> Dict:
        """
        Добавить силовую тренировку в неделю.

        Args:
            start_date: Начало недели
            competition_date: Дата соревнования
            user_preferred_days: Предпочтительные дни пользователя
            week_workouts: Список уже запланированных тренировок на неделю

        Returns:
            Dict: Данные силовой тренировки или None
        """
        # Предпочтительные дни для тренировок
        if user_preferred_days and len(user_preferred_days) > 0:
            preferred_days = sorted(user_preferred_days)
        else:
            preferred_days = [0, 1, 2, 3, 4, 5, 6]

        # Рассчитать понедельник текущей недели
        days_since_monday = start_date.weekday()
        monday_of_week = start_date - timedelta(days=days_since_monday)

        # Группировка тренировок по дням недели
        workouts_by_day = {}
        for workout in week_workouts:
            workout_date = workout['date']
            if isinstance(workout_date, str):
                workout_date = date.fromisoformat(workout_date)
            day_of_week = workout_date.weekday()
            if day_of_week not in workouts_by_day:
                workouts_by_day[day_of_week] = []
            workouts_by_day[day_of_week].append(workout)

        # СТРАТЕГИЯ 1: Найти свободный предпочтительный день
        for preferred_day in preferred_days:
            if preferred_day not in workouts_by_day:
                workout_date = monday_of_week + timedelta(days=preferred_day)

                # Если дата в прошлом, перенести на следующую неделю
                if workout_date < start_date:
                    workout_date = workout_date + timedelta(days=7)

                # Проверить, что дата не превышает дату соревнования
                if workout_date < competition_date:
                    return {
                        'date': workout_date,
                        'sport_type': SportType.STRENGTH,
                        'duration_minutes': 50,
                        'workout_type': WorkoutType.RECOVERY
                    }

        # СТРАТЕГИЯ 2: Если все дни заняты, добавить в день с минимальной нагрузкой
        # Это нормально для триатлона - можно делать силовую и бег/плавание/велосипед в один день
        min_duration = float('inf')
        best_day = None
        best_date = None

        for preferred_day in preferred_days:
            workout_date = monday_of_week + timedelta(days=preferred_day)

            # Проверить условия даты
            if workout_date < start_date:
                workout_date = workout_date + timedelta(days=7)

            if workout_date >= competition_date:
                continue

            # Рассчитать суммарную продолжительность тренировок в этот день
            day_duration = sum(w['duration_minutes'] for w in workouts_by_day.get(preferred_day, []))

            # Найти день с минимальной нагрузкой
            if day_duration < min_duration:
                min_duration = day_duration
                best_day = preferred_day
                best_date = workout_date

        # Если нашли подходящий день, добавляем силовую
        if best_date:
            return {
                'date': best_date,
                'sport_type': SportType.STRENGTH,
                'duration_minutes': 50,
                'workout_type': WorkoutType.RECOVERY
            }

        return None

    def get_plan_by_uin(self, uin: str) -> TrainingPlan:
        """Получить план тренировок пользователя"""
        user = self.db.query(User).filter(User.uin == uin).first()
        if not user:
            return None
        
        return self.db.query(TrainingPlan).filter(TrainingPlan.user_id == user.id).first()
    
    def get_workouts_by_date_range(self, uin: str, start_date: date, end_date: date) -> List[Dict]:
        """Получить тренировки пользователя в указанном диапазоне дат с информацией о выполнении"""
        user = self.db.query(User).filter(User.uin == uin).first()
        if not user:
            return []

        plan = self.db.query(TrainingPlan).filter(TrainingPlan.user_id == user.id).first()
        if not plan:
            return []

        # Получить тренировки
        workouts = self.db.query(Workout).filter(
            Workout.plan_id == plan.id,
            Workout.date >= start_date,
            Workout.date <= end_date
        ).order_by(Workout.date).all()

        # Получить все отметки выполнения для этих тренировок
        workout_ids = [w.id for w in workouts]
        completion_marks = {}
        if workout_ids:
            marks = self.db.query(WorkoutCompletionMark).filter(
                WorkoutCompletionMark.workout_id.in_(workout_ids),
                WorkoutCompletionMark.user_id == user.id
            ).all()
            completion_marks = {mark.workout_id: True for mark in marks}

        # Создать список словарей с информацией о выполнении
        workout_responses = []
        for workout in workouts:
            workout_responses.append({
                'id': workout.id,
                'date': workout.date,
                'sport_type': workout.sport_type,
                'duration_minutes': workout.duration_minutes,
                'workout_type': workout.workout_type,
                'is_completed': completion_marks.get(workout.id, False),
                'is_custom': bool(workout.is_custom) if hasattr(workout, 'is_custom') else False
            })

        return workout_responses
    
    def delete_user_plan(self, uin: str) -> bool:
        """Удалить план пользователя"""
        user = self.db.query(User).filter(User.uin == uin).first()
        if not user:
            return False
        
        plan = self.db.query(TrainingPlan).filter(TrainingPlan.user_id == user.id).first()
        if not plan:
            return False
        
        # Удаление плана автоматически удалит связанные тренировки (cascade)
        self.db.delete(plan)
        self.db.commit()
        
        return True
    
    def update_workout_date(self, uin: str, workout_id: int, new_date: date) -> bool:
        """Обновить дату тренировки"""
        user = self.db.query(User).filter(User.uin == uin).first()
        if not user:
            return False
        
        plan = self.db.query(TrainingPlan).filter(TrainingPlan.user_id == user.id).first()
        if not plan:
            return False
        
        # Найти тренировку, принадлежащую плану пользователя
        workout = self.db.query(Workout).filter(
            Workout.id == workout_id,
            Workout.plan_id == plan.id
        ).first()
        
        if not workout:
            return False
        
        # Обновить дату тренировки
        workout.date = new_date
        self.db.commit()
        
        return True