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
    # Предпочтительные дни для тренировок (JSON строка с массивом дней недели: 0=понедельник, 6=воскресенье)
    preferred_workout_days = Column(String, nullable=True, default="[0,1,2,3,4,5,6]")
    # Информация о соревновании пользователя
    competition_date = Column(Date, nullable=True)
    competition_type = Column(Enum(CompetitionType), nullable=True)
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

# Обеспечение совместимости базы данных
def ensure_database_compatibility():
    """
    Обеспечить совместимость базы данных с текущей схемой
    Эта функция должна вызываться при каждом запуске приложения
    """
    
    print(f"Ensuring database compatibility for: {DB_PATH}")
    
    try:
        # Проверяем, существует ли база данных
        if not os.path.exists(DB_PATH):
            print("Database does not exist, will be created by SQLAlchemy")
            return
        
        # Подключаемся через sqlite3 для проверки схемы
        import sqlite3
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Проверяем существование таблицы users
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
        if not cursor.fetchone():
            print("Users table does not exist, will be created by SQLAlchemy")
            conn.close()
            return
        
        # Получаем текущую схему таблицы users
        cursor.execute("PRAGMA table_info(users);")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print(f"Current columns in users table: {column_names}")
        
        # Определяем необходимые колонки
        required_columns = {
            'competition_date': 'DATE',
            'competition_type': 'VARCHAR'
        }
        
        # Находим отсутствующие колонки
        missing_columns = []
        for col_name, col_type in required_columns.items():
            if col_name not in column_names:
                missing_columns.append((col_name, col_type))
        
        if missing_columns:
            print(f"Found missing columns: {[col[0] for col in missing_columns]}")
            
            # Добавляем отсутствующие колонки
            for col_name, col_type in missing_columns:
                try:
                    alter_sql = f"ALTER TABLE users ADD COLUMN {col_name} {col_type};"
                    print(f"Executing: {alter_sql}")
                    cursor.execute(alter_sql)
                    print(f"✅ Added column: {col_name}")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" in str(e).lower():
                        print(f"⚠️  Column {col_name} already exists")
                    else:
                        print(f"❌ Error adding column {col_name}: {e}")
                        raise
            
            conn.commit()
            print("✅ Database schema updated successfully")
        else:
            print("✅ All required columns are present")
        
        # Проверяем финальную схему
        cursor.execute("PRAGMA table_info(users);")
        final_columns = cursor.fetchall()
        final_column_names = [col[1] for col in final_columns]
        
        # Убеждаемся, что все необходимые колонки присутствуют
        for col_name in required_columns.keys():
            if col_name not in final_column_names:
                raise Exception(f"Column {col_name} is still missing after migration!")
        
        conn.close()
        
        # Очищаем метаданные SQLAlchemy для избежания кэширования
        Base.metadata.clear()
        
        print("✅ Database compatibility check completed")
        
    except Exception as e:
        print(f"❌ Error ensuring database compatibility: {e}")
        import traceback
        traceback.print_exc()
        # Не поднимаем исключение, чтобы не прерывать запуск приложения

# Создание таблиц
def create_tables():
    try:
        print("Creating database tables...")
        
        # Создаем все таблицы
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
