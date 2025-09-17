"""
Генератор персонализированных планов тренировок
"""

from typing import List, Dict
from datetime import date, timedelta
from sqlalchemy.orm import Session
import random

from database import User, TrainingPlan, Workout, CompetitionType, WorkoutCompletionMark
from training_tables import TrainingTables
from schemas import TrainingPlanCreate

class PlanGenerator:
    """Класс для генерации персонализированных планов тренировок"""
    
    def __init__(self, db: Session):
        self.db = db
        self.training_tables = TrainingTables()
    
    def create_training_plan(self, plan_data: TrainingPlanCreate) -> TrainingPlan:
        """Создать персонализированный план тренировок"""
        
        # Найти или создать пользователя
        user = self.db.query(User).filter(User.uin == plan_data.uin).first()
        if not user:
            # Создаем пользователя с минимальными данными для генерации плана
            import json
            user = User(
                uin=plan_data.uin,
                email=f"{plan_data.uin}@triplan.local",  # Временный email для генерации планов
                hashed_password="temp_hash",  # Временный хеш пароля
                preferred_workout_days=json.dumps([0, 1, 2, 4, 5, 6])  # Значение по умолчанию
            )
            self.db.add(user)
            self.db.flush()  # Получить ID пользователя
        
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
            
            # Перейти к следующей неделе (к понедельнику)
            days_since_monday = current_date.weekday()  # 0 = понедельник, 6 = воскресенье
            current_date = current_date + timedelta(days=7 - days_since_monday)
        
        # Фильтровать все тренировки по предпочтительным дням пользователя
        filtered_workouts = self._filter_workouts_by_preferred_days(workouts, plan.user_id)
        return filtered_workouts
    
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
            else:
                # Перенести тренировку на ближайший предпочтительный день
                moved_workout = self._move_workout_to_preferred_day(workout, preferred_days)
                if moved_workout:
                    filtered_workouts.append(moved_workout)
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
            return [0, 1, 2, 4, 5, 6]  # Значение по умолчанию
        
        try:
            import json
            preferred_days = json.loads(user.preferred_workout_days)
            return preferred_days
        except (json.JSONDecodeError, TypeError):
            return [0, 1, 2, 4, 5, 6]  # Fallback к значению по умолчанию
    
    def _schedule_weekly_workouts(self, weekly_workouts: List, start_date: date, 
                                competition_date: date, user_preferred_days: List[int] = None) -> List[Dict]:
        """Распределить тренировки по дням недели"""
        scheduled_workouts = []
        
        # Предпочтительные дни для тренировок (понедельник = 0, воскресенье = 6)
        if user_preferred_days is not None:
            preferred_days = user_preferred_days
        else:
            preferred_days = [0, 1, 2, 4, 5, 6]  # Исключаем среду как день отдыха (значение по умолчанию)
        
        # Перемешать тренировки для разнообразия
        shuffled_workouts = weekly_workouts.copy()
        random.shuffle(shuffled_workouts)
        
        # Распределить тренировки по дням
        for i, (sport_type, workout_type, duration) in enumerate(shuffled_workouts):
            # Выбрать день недели из предпочтительных дней
            preferred_day = preferred_days[i % len(preferred_days)]
            
            # Рассчитать смещение от начала недели (понедельник = 0)
            # start_date может быть любым днем недели, нужно найти понедельник этой недели
            days_since_monday = start_date.weekday()  # 0 = понедельник, 6 = воскресенье
            monday_of_week = start_date - timedelta(days=days_since_monday)
            
            # Добавить смещение до выбранного дня недели
            workout_date = monday_of_week + timedelta(days=preferred_day)
            
            # Если дата тренировки в прошлом, НЕ переносить на следующую неделю,
            # а распределить по предпочтительным дням текущей недели
            if workout_date < start_date:
                # Найти ближайший предпочтительный день в текущей неделе
                current_week_preferred_days = []
                for day in preferred_days:
                    day_date = monday_of_week + timedelta(days=day)
                    if day_date >= start_date:
                        current_week_preferred_days.append(day)
                
                if current_week_preferred_days:
                    # Использовать предпочтительный день из текущей недели
                    preferred_day = current_week_preferred_days[i % len(current_week_preferred_days)]
                    workout_date = monday_of_week + timedelta(days=preferred_day)
                else:
                    # Если нет подходящих дней в текущей неделе, пропустить тренировку
                    continue
            
            # Убедиться, что дата не превышает дату соревнования
            if workout_date >= competition_date:
                continue
            
            scheduled_workouts.append({
                'date': workout_date,
                'sport_type': sport_type,
                'duration_minutes': duration,
                'workout_type': workout_type
            })
        
        return scheduled_workouts
    
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
        
        # Фильтровать тренировки по предпочтительным дням пользователя
        filtered_workouts = self._filter_workouts_by_preferred_days_from_db(workouts, user.id)
        
        # Создать список словарей с информацией о выполнении
        workout_responses = []
        for workout in filtered_workouts:
            workout_responses.append({
                'id': workout.id,
                'date': workout.date,
                'sport_type': workout.sport_type,
                'duration_minutes': workout.duration_minutes,
                'workout_type': workout.workout_type,
                'is_completed': completion_marks.get(workout.id, False)
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