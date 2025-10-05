"""
API endpoints для администрирования
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from database import get_db, User, Tariff, TariffType, WorkoutCoefficients, AppSettings, Base, engine
from auth import get_current_admin_user, get_password_hash
from schemas import (
    AdminUserResponse, UserTariffUpdate, TariffResponse, TariffsUpdateRequest,
    WorkoutCoefficientsResponse, WorkoutCoefficientsUpdate, AppSettingResponse, AppSettingUpdate
)
import uuid
from sqlalchemy import text

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])

# Пользователи
@router.get("/users", response_model=List[AdminUserResponse])
async def get_all_users(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """Получить список всех пользователей"""
    users = db.query(User).all()
    
    result = []
    for user in users:
        tariff_type = None
        tariff_name = None
        if user.tariff:
            tariff_type = user.tariff.type
            tariff_name = user.tariff.name
        
        result.append(AdminUserResponse(
            id=user.id,
            uin=user.uin,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=bool(user.is_active),
            tariff_type=tariff_type,
            tariff_name=tariff_name,
            created_at=user.created_at
        ))
    
    return result

@router.put("/users/tariff")
async def update_user_tariff(
    request: UserTariffUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """Обновить тариф пользователя"""
    print(f"Обновление тарифа пользователя {request.user_id} на {request.tariff_type}")
    
    try:
        # Найти пользователя
        user = db.query(User).filter(User.id == request.user_id).first()
        if not user:
            print(f"Пользователь с ID {request.user_id} не найден")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        
        print(f"Пользователь найден: {user.email}")
        
        # Найти тариф
        tariff = db.query(Tariff).filter(Tariff.type == request.tariff_type).first()
        if not tariff:
            print(f"Тариф {request.tariff_type} не найден")
            # Попробуем создать тарифы, если их нет
            try:
                from database import Base, engine
                Base.metadata.create_all(bind=engine)
                
                # Создаем тарифы по умолчанию
                tariffs_data = [
                    {"name": "Тестовый", "type": TariffType.TEST, "view_full_plan": 0, "view_two_weeks": 1},
                    {"name": "Пробный", "type": TariffType.TRIAL, "view_full_plan": 0, "view_two_weeks": 1},
                    {"name": "Про", "type": TariffType.PRO, "view_full_plan": 1, "view_two_weeks": 1}
                ]
                
                for tariff_data in tariffs_data:
                    existing = db.query(Tariff).filter(Tariff.type == tariff_data["type"]).first()
                    if not existing:
                        new_tariff = Tariff(**tariff_data)
                        db.add(new_tariff)
                
                db.commit()
                
                # Попробуем найти тариф снова
                tariff = db.query(Tariff).filter(Tariff.type == request.tariff_type).first()
                
            except Exception as create_error:
                print(f"Ошибка создания тарифов: {create_error}")
                
            if not tariff:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Тариф {request.tariff_type} не найден и не может быть создан"
                )
        
        print(f"Тариф найден: {tariff.name} (ID: {tariff.id})")
        
        # Обновить тариф пользователя
        user.tariff_id = tariff.id
        user.updated_at = datetime.utcnow()
        db.commit()
        
        print(f"Тариф пользователя {user.email} обновлен на {tariff.name}")
        return {"message": "Тариф пользователя успешно обновлен"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Ошибка при обновлении тарифа: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обновлении тарифа: {str(e)}"
        )

# Тарифы
@router.get("/tariffs", response_model=List[TariffResponse])
async def get_all_tariffs(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """Получить список всех тарифов"""
    tariffs = db.query(Tariff).all()
    
    result = []
    for tariff in tariffs:
        result.append(TariffResponse(
            id=tariff.id,
            name=tariff.name,
            type=tariff.type,
            view_full_plan=bool(tariff.view_full_plan),
            view_two_weeks=bool(tariff.view_two_weeks),
            created_at=tariff.created_at,
            updated_at=tariff.updated_at
        ))
    
    return result

@router.put("/tariffs")
async def update_tariffs(
    request: TariffsUpdateRequest,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """Обновить настройки всех тарифов"""
    
    # Обновить тестовый тариф
    test_tariff = db.query(Tariff).filter(Tariff.type == TariffType.TEST).first()
    if test_tariff:
        test_tariff.view_full_plan = int(request.test.view_full_plan)
        test_tariff.view_two_weeks = int(request.test.view_two_weeks)
        test_tariff.updated_at = datetime.utcnow()
    
    # Обновить пробный тариф
    trial_tariff = db.query(Tariff).filter(Tariff.type == TariffType.TRIAL).first()
    if trial_tariff:
        trial_tariff.view_full_plan = int(request.trial.view_full_plan)
        trial_tariff.view_two_weeks = int(request.trial.view_two_weeks)
        trial_tariff.updated_at = datetime.utcnow()
    
    # Обновить про тариф
    pro_tariff = db.query(Tariff).filter(Tariff.type == TariffType.PRO).first()
    if pro_tariff:
        pro_tariff.view_full_plan = int(request.pro.view_full_plan)
        pro_tariff.view_two_weeks = int(request.pro.view_two_weeks)
        pro_tariff.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Настройки тарифов успешно обновлены"}

# Коэффициенты тренировок
@router.get("/workout-coefficients", response_model=WorkoutCoefficientsResponse)
async def get_workout_coefficients(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """Получить коэффициенты тренировок"""
    print("Запрос коэффициентов тренировок от администратора:", admin_user.email)
    
    try:
        coefficients = db.query(WorkoutCoefficients).first()
        print(f"Найдено коэффициентов в БД: {coefficients is not None}")
        
        if not coefficients:
            print("Создание коэффициентов по умолчанию...")
            # Создать коэффициенты по умолчанию, если их нет
            coefficients = WorkoutCoefficients()
            db.add(coefficients)
            db.commit()
            db.refresh(coefficients)
            print("Коэффициенты созданы с ID:", coefficients.id)
    except Exception as e:
        # Если таблица не существует, создаем её и коэффициенты
        print(f"Ошибка при получении коэффициентов: {e}")
        try:
            # Создаем таблицы, если их нет
            from database import Base, engine
            Base.metadata.create_all(bind=engine)
            
            # Создаем коэффициенты по умолчанию
            coefficients = WorkoutCoefficients()
            db.add(coefficients)
            db.commit()
            db.refresh(coefficients)
        except Exception as create_error:
            print(f"Ошибка при создании коэффициентов: {create_error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при получении коэффициентов тренировок: {str(create_error)}"
            )
    
    return WorkoutCoefficientsResponse(
        id=coefficients.id,
        weekly_distance_beginner=coefficients.weekly_distance_beginner,
        weekly_distance_5_10=coefficients.weekly_distance_5_10,
        weekly_distance_10_30=coefficients.weekly_distance_10_30,
        weekly_distance_30_50=coefficients.weekly_distance_30_50,
        weekly_distance_50_plus=coefficients.weekly_distance_50_plus,
        pace_8_plus=coefficients.pace_8_plus,
        pace_7_8=coefficients.pace_7_8,
        pace_6_7=coefficients.pace_6_7,
        pace_5_6=coefficients.pace_5_6,
        pace_4_5=coefficients.pace_4_5,
        pace_4_minus=coefficients.pace_4_minus,
        target_distance_5k=coefficients.target_distance_5k,
        target_distance_10k=coefficients.target_distance_10k,
        target_distance_21k=coefficients.target_distance_21k,
        target_distance_42k=coefficients.target_distance_42k,
        time_preparation_base=coefficients.time_preparation_base,
        time_preparation_weeks_optimal=coefficients.time_preparation_weeks_optimal,
        created_at=coefficients.created_at,
        updated_at=coefficients.updated_at
    )

@router.put("/workout-coefficients")
async def update_workout_coefficients(
    request: WorkoutCoefficientsUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """Обновить коэффициенты тренировок"""
    coefficients = db.query(WorkoutCoefficients).first()
    
    if not coefficients:
        # Создать новые коэффициенты
        coefficients = WorkoutCoefficients()
        db.add(coefficients)
    
    # Обновить все коэффициенты
    coefficients.weekly_distance_beginner = request.weekly_distance_beginner
    coefficients.weekly_distance_5_10 = request.weekly_distance_5_10
    coefficients.weekly_distance_10_30 = request.weekly_distance_10_30
    coefficients.weekly_distance_30_50 = request.weekly_distance_30_50
    coefficients.weekly_distance_50_plus = request.weekly_distance_50_plus
    
    coefficients.pace_8_plus = request.pace_8_plus
    coefficients.pace_7_8 = request.pace_7_8
    coefficients.pace_6_7 = request.pace_6_7
    coefficients.pace_5_6 = request.pace_5_6
    coefficients.pace_4_5 = request.pace_4_5
    coefficients.pace_4_minus = request.pace_4_minus
    
    coefficients.target_distance_5k = request.target_distance_5k
    coefficients.target_distance_10k = request.target_distance_10k
    coefficients.target_distance_21k = request.target_distance_21k
    coefficients.target_distance_42k = request.target_distance_42k
    
    coefficients.time_preparation_base = request.time_preparation_base
    coefficients.time_preparation_weeks_optimal = request.time_preparation_weeks_optimal
    
    coefficients.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Коэффициенты тренировок успешно обновлены"}

# Проверка прав администратора
@router.get("/check-admin")
async def check_admin_rights(
    admin_user: User = Depends(get_current_admin_user)
):
    """Проверить права администратора"""
    return {
        "is_admin": True,
        "user_email": admin_user.email,
        "message": "Права администратора подтверждены"
    }

# Исправление проблем админки
@router.post("/fix-issues")
async def fix_admin_issues(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """Исправить все проблемы админки"""
    results = []
    
    try:
        # 1. Создаем все таблицы, если их нет
        results.append("📋 Создание таблиц...")
        
        # Сначала пробуем стандартный способ
        try:
            Base.metadata.create_all(bind=engine)
            results.append("✅ Стандартное создание таблиц выполнено")
        except Exception as create_error:
            results.append(f"⚠️ Ошибка стандартного создания: {create_error}")
        
        # Проверяем и создаем таблицы вручную, если нужно
        try:
            # Проверяем существование таблицы tariffs
            result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='tariffs'"))
            if not result.fetchone():
                results.append("➕ Создание таблицы tariffs...")
                db.execute(text("""
                    CREATE TABLE tariffs (
                        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                        name VARCHAR NOT NULL,
                        type VARCHAR NOT NULL UNIQUE,
                        view_full_plan INTEGER DEFAULT 0,
                        view_two_weeks INTEGER DEFAULT 1,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                db.commit()
                results.append("✅ Таблица tariffs создана")
            else:
                results.append("✅ Таблица tariffs уже существует")
            
            # Проверяем существование таблицы workout_coefficients
            result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='workout_coefficients'"))
            if not result.fetchone():
                results.append("➕ Создание таблицы workout_coefficients...")
                db.execute(text("""
                    CREATE TABLE workout_coefficients (
                        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                        weekly_distance_beginner INTEGER DEFAULT 10,
                        weekly_distance_5_10 INTEGER DEFAULT 50,
                        weekly_distance_10_30 INTEGER DEFAULT 100,
                        weekly_distance_30_50 INTEGER DEFAULT 200,
                        weekly_distance_50_plus INTEGER DEFAULT 300,
                        pace_8_plus INTEGER DEFAULT 20,
                        pace_7_8 INTEGER DEFAULT 50,
                        pace_6_7 INTEGER DEFAULT 100,
                        pace_5_6 INTEGER DEFAULT 150,
                        pace_4_5 INTEGER DEFAULT 200,
                        pace_4_minus INTEGER DEFAULT 300,
                        target_distance_5k INTEGER DEFAULT 50,
                        target_distance_10k INTEGER DEFAULT 100,
                        target_distance_21k INTEGER DEFAULT 150,
                        target_distance_42k INTEGER DEFAULT 250,
                        time_preparation_base INTEGER DEFAULT 100,
                        time_preparation_weeks_optimal INTEGER DEFAULT 16,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                db.commit()
                results.append("✅ Таблица workout_coefficients создана")
            else:
                results.append("✅ Таблица workout_coefficients уже существует")
                
        except Exception as manual_create_error:
            results.append(f"⚠️ Ошибка ручного создания таблиц: {manual_create_error}")
        
        results.append("✅ Проверка таблиц завершена")
        
        # 2. Исправляем тарифы
        results.append("💳 Исправление тарифов...")
        
        # Проверяем колонку tariff_id в таблице users
        try:
            result = db.execute(text("PRAGMA table_info(users)"))
            columns = [row[1] for row in result.fetchall()]
            
            if 'tariff_id' not in columns:
                results.append("➕ Добавление колонки tariff_id...")
                db.execute(text("ALTER TABLE users ADD COLUMN tariff_id INTEGER"))
                db.commit()
                results.append("✅ Колонка tariff_id добавлена")
            else:
                results.append("✅ Колонка tariff_id уже существует")
                
        except Exception as column_error:
            results.append(f"⚠️ Ошибка проверки колонки: {column_error}")
        
        # Создаем тарифы
        try:
            tariffs_count = db.query(Tariff).count()
            results.append(f"📊 Найдено тарифов: {tariffs_count}")
        except Exception as count_error:
            results.append(f"⚠️ Ошибка подсчета тарифов: {count_error}")
            tariffs_count = 0
            
        if tariffs_count == 0:
            results.append("⚙️ Создание тарифов по умолчанию...")
            
            tariffs_data = [
                {"name": "Тестовый", "type": TariffType.TEST, "view_full_plan": 0, "view_two_weeks": 1},
                {"name": "Пробный", "type": TariffType.TRIAL, "view_full_plan": 0, "view_two_weeks": 1},
                {"name": "Про", "type": TariffType.PRO, "view_full_plan": 1, "view_two_weeks": 1}
            ]
            
            for tariff_data in tariffs_data:
                tariff = Tariff(**tariff_data)
                db.add(tariff)
            
            db.commit()
            results.append("✅ Тарифы созданы")
        else:
            results.append("✅ Тарифы уже существуют")
        
        # Назначаем тариф пользователям без тарифа
        users_without_tariff = db.query(User).filter(User.tariff_id.is_(None)).count()
        if users_without_tariff > 0:
            test_tariff = db.query(Tariff).filter(Tariff.type == TariffType.TEST).first()
            if test_tariff:
                db.execute(
                    text("UPDATE users SET tariff_id = :tariff_id WHERE tariff_id IS NULL"),
                    {"tariff_id": test_tariff.id}
                )
                db.commit()
                results.append(f"✅ Назначен тестовый тариф {users_without_tariff} пользователям")
        
        # 3. Исправляем коэффициенты
        results.append("⚙️ Исправление коэффициентов...")
        
        try:
            coefficients = db.query(WorkoutCoefficients).first()
            results.append(f"📊 Коэффициенты найдены: {coefficients is not None}")
        except Exception as coeff_error:
            results.append(f"⚠️ Ошибка поиска коэффициентов: {coeff_error}")
            coefficients = None
            
        if not coefficients:
            results.append("⚙️ Создание коэффициентов по умолчанию...")
            coefficients = WorkoutCoefficients(
                weekly_distance_beginner=10,
                weekly_distance_5_10=50,
                weekly_distance_10_30=100,
                weekly_distance_30_50=200,
                weekly_distance_50_plus=300,
                pace_8_plus=20,
                pace_7_8=50,
                pace_6_7=100,
                pace_5_6=150,
                pace_4_5=200,
                pace_4_minus=300,
                target_distance_5k=50,
                target_distance_10k=100,
                target_distance_21k=150,
                target_distance_42k=250,
                time_preparation_base=100,
                time_preparation_weeks_optimal=16
            )
            db.add(coefficients)
            db.commit()
            results.append("✅ Коэффициенты созданы")
        else:
            results.append("✅ Коэффициенты уже существуют")
        
        # 4. Создаем администратора
        results.append("👤 Проверка администратора...")
        
        admin_check = db.query(User).filter(User.email == "abramov.yu.v@gmail.com").first()
        if not admin_check:
            results.append("⚙️ Создание пользователя-администратора...")
            admin_uin = str(uuid.uuid4())
            while db.query(User).filter(User.uin == admin_uin).first():
                admin_uin = str(uuid.uuid4())
            
            new_admin = User(
                uin=admin_uin,
                email="abramov.yu.v@gmail.com",
                hashed_password=get_password_hash("admin123"),
                first_name="Юрий",
                last_name="Абрамов",
                is_active=1
            )
            db.add(new_admin)
            db.commit()
            results.append("✅ Администратор создан")
            results.append("   📧 Email: abramov.yu.v@gmail.com")
            results.append("   🔑 Пароль: admin123")
        else:
            results.append("✅ Администратор уже существует")
        
        # Статистика
        results.append("📊 Итоговая статистика:")
        results.append(f"   • Тарифов: {db.query(Tariff).count()}")
        results.append(f"   • Пользователей: {db.query(User).count()}")
        results.append(f"   • Коэффициентов: {db.query(WorkoutCoefficients).count()}")
        
        results.append("🎉 Все проблемы админки исправлены успешно!")
        
        return {
            "success": True,
            "message": "Все проблемы админки исправлены успешно!",
            "details": results
        }
        
    except Exception as e:
        db.rollback()
        results.append(f"❌ Ошибка: {str(e)}")
        return {
            "success": False,
            "message": f"Ошибка при исправлении проблем: {str(e)}",
            "details": results
        }

# Создание только таблиц (упрощенная версия)
@router.post("/create-tables")
async def create_admin_tables(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """Создать только таблицы админки"""
    results = []
    
    try:
        results.append("📋 Создание таблиц админки...")
        
        # Создание таблицы tariffs
        try:
            result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='tariffs'"))
            if not result.fetchone():
                results.append("➕ Создание таблицы tariffs...")
                db.execute(text("""
                    CREATE TABLE tariffs (
                        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                        name VARCHAR NOT NULL,
                        type VARCHAR NOT NULL UNIQUE,
                        view_full_plan INTEGER DEFAULT 0,
                        view_two_weeks INTEGER DEFAULT 1,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                db.commit()
                results.append("✅ Таблица tariffs создана")
            else:
                results.append("✅ Таблица tariffs уже существует")
        except Exception as tariff_error:
            results.append(f"❌ Ошибка создания tariffs: {tariff_error}")
        
        # Создание таблицы workout_coefficients
        try:
            result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='workout_coefficients'"))
            if not result.fetchone():
                results.append("➕ Создание таблицы workout_coefficients...")
                db.execute(text("""
                    CREATE TABLE workout_coefficients (
                        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                        weekly_distance_beginner INTEGER DEFAULT 10,
                        weekly_distance_5_10 INTEGER DEFAULT 50,
                        weekly_distance_10_30 INTEGER DEFAULT 100,
                        weekly_distance_30_50 INTEGER DEFAULT 200,
                        weekly_distance_50_plus INTEGER DEFAULT 300,
                        pace_8_plus INTEGER DEFAULT 20,
                        pace_7_8 INTEGER DEFAULT 50,
                        pace_6_7 INTEGER DEFAULT 100,
                        pace_5_6 INTEGER DEFAULT 150,
                        pace_4_5 INTEGER DEFAULT 200,
                        pace_4_minus INTEGER DEFAULT 300,
                        target_distance_5k INTEGER DEFAULT 50,
                        target_distance_10k INTEGER DEFAULT 100,
                        target_distance_21k INTEGER DEFAULT 150,
                        target_distance_42k INTEGER DEFAULT 250,
                        time_preparation_base INTEGER DEFAULT 100,
                        time_preparation_weeks_optimal INTEGER DEFAULT 16,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                db.commit()
                results.append("✅ Таблица workout_coefficients создана")
            else:
                results.append("✅ Таблица workout_coefficients уже существует")
        except Exception as coeff_error:
            results.append(f"❌ Ошибка создания workout_coefficients: {coeff_error}")
        
        # Добавление колонки tariff_id в users
        try:
            result = db.execute(text("PRAGMA table_info(users)"))
            columns = [row[1] for row in result.fetchall()]
            
            if 'tariff_id' not in columns:
                results.append("➕ Добавление колонки tariff_id в users...")
                db.execute(text("ALTER TABLE users ADD COLUMN tariff_id INTEGER"))
                db.commit()
                results.append("✅ Колонка tariff_id добавлена")
            else:
                results.append("✅ Колонка tariff_id уже существует")
        except Exception as column_error:
            results.append(f"❌ Ошибка добавления колонки: {column_error}")
        
        results.append("🎉 Создание таблиц завершено!")
        
        return {
            "success": True,
            "message": "Таблицы админки созданы успешно!",
            "details": results
        }
        
    except Exception as e:
        db.rollback()
        results.append(f"❌ Критическая ошибка: {str(e)}")
        return {
            "success": False,
            "message": f"Ошибка при создании таблиц: {str(e)}",
            "details": results
        }

# Настройки приложения
@router.get("/settings", response_model=List[AppSettingResponse])
async def get_app_settings(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """Получить все настройки приложения"""
    settings = db.query(AppSettings).all()
    return settings

@router.get("/settings/{key}", response_model=AppSettingResponse)
async def get_app_setting(
    key: str,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """Получить настройку по ключу"""
    setting = db.query(AppSettings).filter(AppSettings.key == key).first()
    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Настройка с ключом '{key}' не найдена"
        )
    return setting

@router.put("/settings/{key}")
async def update_app_setting(
    key: str,
    setting_update: AppSettingUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """Обновить настройку приложения"""
    setting = db.query(AppSettings).filter(AppSettings.key == key).first()
    
    if not setting:
        # Создать новую настройку
        setting = AppSettings(
            key=setting_update.key,
            value=setting_update.value,
            description=setting_update.description
        )
        db.add(setting)
    else:
        # Обновить существующую
        setting.value = setting_update.value
        if setting_update.description is not None:
            setting.description = setting_update.description
        setting.updated_at = datetime.utcnow()
    
    db.commit()
    return {"message": "Настройка успешно обновлена"}

@router.post("/settings/init")
async def init_default_settings(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """Инициализировать настройки по умолчанию"""
    default_settings = [
        {
            "key": "pro_tariff_price",
            "value": "999.00",
            "description": "Цена тарифа Про за месяц (в рублях)"
        }
    ]
    
    created_count = 0
    for setting_data in default_settings:
        existing = db.query(AppSettings).filter(AppSettings.key == setting_data["key"]).first()
        if not existing:
            setting = AppSettings(**setting_data)
            db.add(setting)
            created_count += 1
    
    db.commit()
    return {"message": f"Создано {created_count} настроек по умолчанию"}
