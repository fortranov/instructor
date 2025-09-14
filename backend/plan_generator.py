"""
Генератор персонализированных планов тренировок
"""

from typing import List, Dict
from datetime import date, timedelta
from sqlalchemy.orm import Session
import random

from database import User, TrainingPlan, Workout, CompetitionType
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
            user = User(uin=plan_data.uin)
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
        
        # Генерировать тренировки
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
        
        # Определить виды спорта для типа соревнования
        sport_types = self.training_tables.get_sport_types_for_competition(plan.competition_type)
        
        # Рассчитать количество недель до соревнования
        today = date.today()
        days_to_competition = (plan.competition_date - today).days
        weeks_to_competition = max(1, days_to_competition // 7)
        
        # Генерировать тренировки по неделям
        current_date = today
        week_count = 0
        
        while current_date < plan.competition_date:
            week_count += 1
            weeks_remaining = max(1, (plan.competition_date - current_date).days // 7)
            
            # Определить фазу тренировки
            phase = self.training_tables.get_training_phase(weeks_remaining)
            
            # Получить недельный объем для основного вида спорта
            primary_sport = sport_types[0]
            weekly_volume = self.training_tables.get_weekly_volume(primary_sport, plan.complexity)
            
            # Скорректировать объем в зависимости от фазы
            volume_multiplier = self._get_volume_multiplier(phase, weeks_remaining)
            adjusted_volume = int(weekly_volume * volume_multiplier)
            
            # Распределить тренировки на неделю
            weekly_workouts = self.training_tables.distribute_weekly_workouts(
                sport_types, adjusted_volume, phase, plan.complexity
            )
            
            # Назначить даты тренировкам в течение недели
            week_workouts = self._schedule_weekly_workouts(
                weekly_workouts, current_date, plan.competition_date
            )
            
            workouts.extend(week_workouts)
            
            # Перейти к следующей неделе
            current_date += timedelta(days=7)
        
        return workouts
    
    def _get_volume_multiplier(self, phase: str, weeks_remaining: int) -> float:
        """Получить множитель объема тренировок в зависимости от фазы"""
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
        
        return base_multiplier
    
    def _schedule_weekly_workouts(self, weekly_workouts: List, start_date: date, 
                                competition_date: date) -> List[Dict]:
        """Распределить тренировки по дням недели"""
        scheduled_workouts = []
        
        # Предпочтительные дни для тренировок (понедельник = 0, воскресенье = 6)
        preferred_days = [0, 1, 2, 4, 5, 6]  # Исключаем среду как день отдыха
        
        # Перемешать тренировки для разнообразия
        shuffled_workouts = weekly_workouts.copy()
        random.shuffle(shuffled_workouts)
        
        # Распределить тренировки по дням
        for i, (sport_type, workout_type, duration) in enumerate(shuffled_workouts):
            # Выбрать день недели
            if i < len(preferred_days):
                day_offset = preferred_days[i]
            else:
                # Если тренировок больше, чем предпочтительных дней
                day_offset = i % 7
            
            # Рассчитать дату тренировки
            workout_date = start_date + timedelta(days=day_offset)
            
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
    
    def get_workouts_by_date_range(self, uin: str, start_date: date, end_date: date) -> List[Workout]:
        """Получить тренировки пользователя в указанном диапазоне дат"""
        user = self.db.query(User).filter(User.uin == uin).first()
        if not user:
            return []
        
        plan = self.db.query(TrainingPlan).filter(TrainingPlan.user_id == user.id).first()
        if not plan:
            return []
        
        return self.db.query(Workout).filter(
            Workout.plan_id == plan.id,
            Workout.date >= start_date,
            Workout.date <= end_date
        ).order_by(Workout.date).all()
    
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
