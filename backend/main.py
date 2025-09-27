"""
Главный файл приложения Triplan Backend Service
Сервис для создания персонализированных планов тренировок
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from database import create_tables, engine
from api_routes import router
from api_completion import completion_router
from api_workouts import workouts_router
from api_statistics import statistics_router
from migrations import run_migrations, check_database_schema
import os

# Создание таблиц при запуске приложения
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_tables()
    
    # Запуск миграций если включена переменная окружения
    if os.getenv("RUN_MIGRATIONS", "false").lower() == "true":
        try:
            run_migrations()
        except Exception as e:
            print(f"Migration failed: {e}")
    
    yield
    # Shutdown
    engine.dispose()

# Создание приложения FastAPI
app = FastAPI(
    title="Triplan Backend Service",
    description="""
    Сервис для создания персонализированных планов тренировок по бегу, велосипеду, плаванию и триатлону.
    
    Основан на методике Джо Фрила и использует принципы периодизации тренировок.
    
    ## Основные возможности:
    
    * **Создание планов** - Персонализированные планы тренировок с учетом сложности и типа соревнования
    * **Получение планов** - Просмотр созданных планов и тренировок по датам
    * **Удаление планов** - Удаление существующих планов пользователей
    
    ## Типы соревнований:
    
    * **Бег**: 10км, полумарафон, марафон
    * **Велосипед**: любая дистанция в километрах
    * **Плавание**: любая дистанция в метрах  
    * **Триатлон**: спринт, олимпийская дистанция, железная дистанция
    
    ## Типы тренировок:
    
    * **Длительная** - развитие выносливости
    * **Интервальная** - развитие скорости и мощности
    * **Восстанавливающая** - активное восстановление
    """,
    version="1.0.0",
    contact={
        "name": "Triplan Support",
        "email": "support@triplan.com",
    },
    license_info={
        "name": "MIT",
    },
    lifespan=lifespan
)

# Настройка CORS для фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене следует указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение маршрутов
app.include_router(router, prefix="/api/v1")
app.include_router(completion_router, prefix="/api/v1")
app.include_router(workouts_router, prefix="/api/v1")
app.include_router(statistics_router, prefix="/api/v1")

# Корневой эндпоинт
@app.get("/")
async def root():
    """
    Корневой эндпоинт сервиса
    """
    return {
        "message": "Добро пожаловать в Triplan Backend Service!",
        "description": "Сервис для создания персонализированных планов тренировок",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health"
    }

# Эндпоинт для миграций (только для администраторов)
@app.post("/api/v1/admin/migrate")
async def run_database_migrations():
    """
    Запустить миграции базы данных
    Требует переменную окружения ADMIN_MIGRATION_TOKEN
    """
    token = os.getenv("ADMIN_MIGRATION_TOKEN")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Migration endpoint disabled"
        )
    
    try:
        run_migrations()
        return {"message": "Migrations completed successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Migration failed: {str(e)}"
        )

@app.get("/api/v1/admin/schema")
async def get_database_schema():
    """
    Получить информацию о схеме базы данных
    """
    try:
        schema = check_database_schema()
        return {"schema": schema}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get schema: {str(e)}"
        )

# Обработчик ошибок
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Глобальный обработчик исключений
    """
    return HTTPException(
        status_code=500,
        detail=f"Внутренняя ошибка сервера: {str(exc)}"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )
