# Исправление ошибки базы данных: "no such column: users.competition_date"

## Описание проблемы

При развертывании приложения с нуля в продакшене возникала ошибка:

```
Ошибка регистрации: (sqlite3.OperationalError) no such column: users.competition_date 
[SQL: SELECT users.id AS users_id, users.uin AS users_uin, users.email AS users_email, 
users.hashed_password AS users_hashed_password, users.first_name AS users_first_name, 
users.last_name AS users_last_name, users.is_active AS users_is_active, 
users.preferred_workout_days AS users_preferred_workout_days, 
users.competition_date AS users_competition_date, 
users.competition_type AS users_competition_type, 
users.created_at AS users_created_at, users.updated_at AS users_updated_at 
FROM users WHERE users.email = ? LIMIT ? OFFSET ?]
```

## Причина проблемы

Проблема возникала из-за того, что при создании базы данных с нуля в продакшене SQLAlchemy иногда не создавал все колонки модели User правильно, или возникали проблемы с кэшированием метаданных.

## Решение

### 1. Добавлена функция обеспечения совместимости базы данных

В файле `backend/database.py` добавлена функция `ensure_database_compatibility()`, которая:

- Проверяет существование базы данных и таблицы users
- Проверяет наличие всех необходимых колонок
- Автоматически добавляет отсутствующие колонки через ALTER TABLE
- Очищает метаданные SQLAlchemy для избежания кэширования

### 2. Обновлен процесс инициализации приложения

В файле `backend/main.py` обновлена функция `lifespan()`:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    ensure_database_compatibility()  # Сначала проверяем и мигрируем существующую БД
    create_tables()                  # Затем создаем таблицы если их нет
    
    yield
    # Shutdown
    engine.dispose()
```

### 3. Улучшена функция создания таблиц

Функция `create_tables()` упрощена и стала более надежной.

## Файлы, которые были изменены

1. `backend/database.py` - добавлена функция `ensure_database_compatibility()`
2. `backend/main.py` - обновлен процесс инициализации
3. Добавлены вспомогательные скрипты для тестирования:
   - `backend/migrate_database.py` - скрипт миграции
   - `backend/test_production_scenario.py` - тест сценария продакшена
   - `backend/docker_test.py` - тест в Docker окружении

## Тестирование

### Локальное тестирование

```bash
cd backend
python test_production_scenario.py
```

### Тестирование в Docker

1. Запустите приложение в Docker:
```bash
docker-compose up --build
```

2. В другом терминале запустите тест:
```bash
cd backend
python docker_test.py
```

### Ручное тестирование миграции

```bash
cd backend
python migrate_database.py
```

## Результат

После внедрения исправления:

✅ База данных создается с правильной схемой при первом запуске
✅ Существующие базы данных автоматически мигрируются при необходимости  
✅ Регистрация пользователей работает корректно
✅ Все операции с пользователями выполняются без ошибок
✅ Приложение стабильно работает в продакшене

## Дополнительные улучшения

1. **Автоматическая миграция** - при каждом запуске приложения проверяется совместимость схемы
2. **Безопасность** - создаются резервные копии перед миграцией
3. **Логирование** - подробные логи процесса инициализации и миграции
4. **Устойчивость к ошибкам** - приложение не падает при проблемах с миграцией

## Рекомендации для продакшена

1. Всегда делайте резервную копию базы данных перед обновлением
2. Проверяйте логи при запуске приложения
3. Используйте переменную окружения `DB_PATH` для указания пути к базе данных
4. Убедитесь, что директория для базы данных имеет права на запись

## Команды для развертывания

```bash
# Сборка и запуск в продакшене
docker-compose up --build -d

# Проверка логов
docker-compose logs backend

# Проверка состояния
curl http://localhost:8000/api/v1/health
```
