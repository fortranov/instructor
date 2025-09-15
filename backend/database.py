from sqlalchemy import create_engine, Column, Integer, String, Float, Date, DateTime, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import enum

# Создание подключения к SQLite
import os

# Определяем путь к базе данных
DB_PATH = os.getenv("DB_PATH", "./triplan.db")

# Создаем директорию для базы данных, если её нет
db_dir = os.path.dirname(os.path.abspath(DB_PATH))
if db_dir and not os.path.exists(db_dir):
    try:
        os.makedirs(db_dir, exist_ok=True)
        print(f"Created database directory: {db_dir}")
    except Exception as e:
        print(f"Error creating database directory {db_dir}: {e}")
        raise

print(f"Database path: {os.path.abspath(DB_PATH)}")
print(f"Database directory exists: {os.path.exists(db_dir)}")
print(f"Database directory writable: {os.access(db_dir, os.W_OK) if os.path.exists(db_dir) else False}")

SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Enums для типов спорта и тренировок
class SportType(str, enum.Enum):
    RUNNING = "running"
    CYCLING = "cycling"
    SWIMMING = "swimming"

class WorkoutType(str, enum.Enum):
    ENDURANCE = "endurance"  # длительная
    INTERVAL = "interval"    # интервальная
    RECOVERY = "recovery"    # восстанавливающая

class CompetitionType(str, enum.Enum):
    # Бег
    RUN_10K = "run_10k"
    RUN_HALF_MARATHON = "run_half_marathon"
    RUN_MARATHON = "run_marathon"
    
    # Велосипед (расстояние в км)
    CYCLING = "cycling"
    
    # Плавание (расстояние в метрах)
    SWIMMING = "swimming"
    
    # Триатлон
    TRIATHLON_SPRINT = "triathlon_sprint"
    TRIATHLON_OLYMPIC = "triathlon_olympic"
    TRIATHLON_IRONMAN = "triathlon_ironman"

# Модель пользователя
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    uin = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    is_active = Column(Integer, default=1)  # SQLite doesn't have Boolean
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связь с планами
    plans = relationship("TrainingPlan", back_populates="user")
    # Связь с отметками выполнения тренировок
    completion_marks = relationship("WorkoutCompletionMark", back_populates="user", cascade="all, delete-orphan")

# Модель плана тренировок
class TrainingPlan(Base):
    __tablename__ = "training_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    complexity = Column(Integer, nullable=False)  # 0-1000
    competition_date = Column(Date, nullable=False)
    competition_type = Column(Enum(CompetitionType), nullable=False)
    competition_distance = Column(Float, nullable=True)  # для велосипеда (км) и плавания (м)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    user = relationship("User", back_populates="plans")
    workouts = relationship("Workout", back_populates="plan", cascade="all, delete-orphan")

# Модель тренировки
class Workout(Base):
    __tablename__ = "workouts"
    
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("training_plans.id"), nullable=False)
    date = Column(Date, nullable=False)
    sport_type = Column(Enum(SportType), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    workout_type = Column(Enum(WorkoutType), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связь с планом
    plan = relationship("TrainingPlan", back_populates="workouts")
    # Связь с отметками выполнения
    completion_marks = relationship("WorkoutCompletionMark", back_populates="workout", cascade="all, delete-orphan")

# Модель отметки выполнения тренировки
class WorkoutCompletionMark(Base):
    __tablename__ = "workout_completion_marks"
    
    id = Column(Integer, primary_key=True, index=True)
    workout_id = Column(Integer, ForeignKey("workouts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)  # Дата когда была отмечена тренировка
    completed_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    workout = relationship("Workout", back_populates="completion_marks")
    user = relationship("User", back_populates="completion_marks")

# Создание таблиц
def create_tables():
    try:
        print("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully!")
    except Exception as e:
        print(f"Error creating database tables: {e}")
        raise

# Получение сессии БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
