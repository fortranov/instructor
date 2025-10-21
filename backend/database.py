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
    # Тариф пользователя
    tariff_id = Column(Integer, ForeignKey("tariffs.id"), nullable=True)
    # Дата окончания тестового периода (для автоматического перехода на неактивный тариф)
    test_period_end_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связь с планами
    plans = relationship("TrainingPlan", back_populates="user")
    # Связь с отметками выполнения тренировок
    completion_marks = relationship("WorkoutCompletionMark", back_populates="user", cascade="all, delete-orphan")
    # Связь с тарифом
    tariff = relationship("Tariff", back_populates="users")

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

# Enum для тарифных планов
class TariffType(str, enum.Enum):
    TEST = "test"  # Тестовый
    TRIAL = "trial"  # Пробный
    PRO = "pro"  # Про
    INACTIVE = "inactive"  # Неактивный (истекший тестовый период)

# Модель тарифного плана
class Tariff(Base):
    __tablename__ = "tariffs"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # Название тарифа
    type = Column(Enum(TariffType), nullable=False, unique=True)  # Тип тарифа
    view_full_plan = Column(Integer, default=0)  # Просмотр всего плана (0/1)
    view_two_weeks = Column(Integer, default=1)  # Просмотр двух недель (0/1)
    # Доступные виды спорта (0/1 для каждого)
    allow_running = Column(Integer, default=1)  # Бег
    allow_cycling = Column(Integer, default=0)  # Велосипед
    allow_swimming = Column(Integer, default=0)  # Плавание
    allow_triathlon = Column(Integer, default=0)  # Триатлон
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связь с пользователями
    users = relationship("User", back_populates="tariff")

# Модель настроек коэффициентов тренировок
class WorkoutCoefficients(Base):
    __tablename__ = "workout_coefficients"
    
    id = Column(Integer, primary_key=True, index=True)
    # Коэффициенты для недельного километража
    weekly_distance_beginner = Column(Integer, default=10)
    weekly_distance_5_10 = Column(Integer, default=50)
    weekly_distance_10_30 = Column(Integer, default=100)
    weekly_distance_30_50 = Column(Integer, default=200)
    weekly_distance_50_plus = Column(Integer, default=300)
    
    # Коэффициенты для комфортного темпа
    pace_8_plus = Column(Integer, default=20)
    pace_7_8 = Column(Integer, default=50)
    pace_6_7 = Column(Integer, default=100)
    pace_5_6 = Column(Integer, default=150)
    pace_4_5 = Column(Integer, default=200)
    pace_4_minus = Column(Integer, default=300)
    
    # Коэффициенты для целевой дистанции
    target_distance_5k = Column(Integer, default=50)
    target_distance_10k = Column(Integer, default=100)
    target_distance_21k = Column(Integer, default=150)
    target_distance_42k = Column(Integer, default=250)
    
    # Коэффициенты для времени подготовки
    time_preparation_base = Column(Integer, default=100)
    time_preparation_weeks_optimal = Column(Integer, default=16)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Модель общих настроек приложения
class AppSettings(Base):
    __tablename__ = "app_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, nullable=False, unique=True)  # Ключ настройки
    value = Column(String, nullable=False)  # Значение настройки
    description = Column(String, nullable=True)  # Описание настройки
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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
            'competition_type': 'VARCHAR',
            'tariff_id': 'INTEGER',
            'test_period_end_date': 'DATETIME'
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
                    print(f"[OK] Added column: {col_name}")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" in str(e).lower():
                        print(f"[WARN] Column {col_name} already exists")
                    else:
                        print(f"[ERROR] Error adding column {col_name}: {e}")
                        raise
            
            conn.commit()
            print("[OK] Database schema updated successfully")
        else:
            print("[OK] All required columns are present")
        
        # Проверяем финальную схему
        cursor.execute("PRAGMA table_info(users);")
        final_columns = cursor.fetchall()
        final_column_names = [col[1] for col in final_columns]
        
        # Убеждаемся, что все необходимые колонки присутствуют
        for col_name in required_columns.keys():
            if col_name not in final_column_names:
                raise Exception(f"Column {col_name} is still missing after migration!")

        # Проверяем и обновляем таблицу tariffs
        print("\nChecking tariffs table...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tariffs';")
        if cursor.fetchone():
            cursor.execute("PRAGMA table_info(tariffs);")
            tariff_columns = cursor.fetchall()
            tariff_column_names = [col[1] for col in tariff_columns]

            print(f"Current columns in tariffs table: {tariff_column_names}")

            # Колонки для видов спорта
            sport_columns = {
                'allow_running': 'INTEGER DEFAULT 1',
                'allow_cycling': 'INTEGER DEFAULT 0',
                'allow_swimming': 'INTEGER DEFAULT 0',
                'allow_triathlon': 'INTEGER DEFAULT 0'
            }

            # Находим отсутствующие колонки
            missing_tariff_columns = []
            for col_name, col_def in sport_columns.items():
                if col_name not in tariff_column_names:
                    missing_tariff_columns.append((col_name, col_def))

            if missing_tariff_columns:
                print(f"Found missing columns in tariffs: {[col[0] for col in missing_tariff_columns]}")

                # Добавляем отсутствующие колонки
                for col_name, col_def in missing_tariff_columns:
                    try:
                        alter_sql = f"ALTER TABLE tariffs ADD COLUMN {col_name} {col_def};"
                        print(f"Executing: {alter_sql}")
                        cursor.execute(alter_sql)
                        print(f"[OK] Added column: {col_name}")
                    except sqlite3.OperationalError as e:
                        if "duplicate column name" in str(e).lower():
                            print(f"[WARN] Column {col_name} already exists")
                        else:
                            print(f"[ERROR] Error adding column {col_name}: {e}")
                            raise

                conn.commit()
                print("[OK] Tariffs table schema updated successfully")

                # Обновляем значения по умолчанию для существующих тарифов
                print("Updating default values for existing tariffs...")
                try:
                    cursor.execute("""
                        UPDATE tariffs
                        SET allow_running = 1
                        WHERE allow_running IS NULL OR allow_running = 0
                    """)

                    # Для PRO тарифа включаем все виды спорта
                    cursor.execute("""
                        UPDATE tariffs
                        SET allow_cycling = 1,
                            allow_swimming = 1,
                            allow_triathlon = 1
                        WHERE type = 'PRO' OR type = 'pro'
                    """)
                    conn.commit()
                    print("[OK] Default values updated for existing tariffs")
                except Exception as update_error:
                    print(f"[WARN] Error updating default values: {update_error}")
            else:
                print("[OK] All required columns are present in tariffs table")
        else:
            print("[WARN] Tariffs table does not exist yet, will be created by SQLAlchemy")

        conn.close()

        print("[OK] Database compatibility check completed")

    except Exception as e:
        print(f"[ERROR] Error ensuring database compatibility: {e}")
        import traceback
        traceback.print_exc()
        # Не поднимаем исключение, чтобы не прерывать запуск приложения

# Создание таблиц
def create_tables():
    try:
        print("Creating database tables...")
        
        # Выводим список таблиц, которые SQLAlchemy собирается создать
        print("Tables in metadata:")
        for table_name in Base.metadata.tables.keys():
            print(f"  - {table_name}")
        
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
