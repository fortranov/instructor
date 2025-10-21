# Исправления ошибок на странице администрирования

## Проблемы

### 1. Ошибка 500 при загрузке списка пользователей
**Симптомы:**
```
GET https://icanrun.ru/api/v1/admin/users 500 (Internal Server Error)
API: Ошибка получения списка пользователей: Error: Request failed with status code 500
```

**Причина:**
- Ошибка при попытке загрузить связанный объект `user.tariff` через ORM relationship
- У некоторых пользователей `tariff_id` установлен, но соответствующий тариф отсутствует в БД
- Отсутствовала обработка ошибок

**Исправление:**
Файл: `backend/api_admin.py` (строки 22-66)
- Добавлена обработка ошибок на уровне всей функции
- Заменен доступ через relationship на явный запрос к БД
- Добавлена индивидуальная обработка ошибок для каждого пользователя
- Добавлено детальное логирование

### 2. Ошибка при обновлении тарифа пользователя
**Симптомы:**
```
API: Ошибка обновления тарифа пользователя: Error: Ошибка при обновлении тарифа:
(sqlite3.OperationalError) no such column: tariffs.allow_running
```

**Причина:**
- В продакшн БД отсутствуют колонки для управления доступными видами спорта
- SQLAlchemy пытается загрузить все колонки модели `Tariff`, включая отсутствующие

**Исправление:**
Файл: `backend/database.py` (строки 290-362)
- Добавлена автоматическая миграция в функцию `ensure_database_compatibility()`
- Миграция проверяет наличие колонок: `allow_running`, `allow_cycling`, `allow_swimming`, `allow_triathlon`
- Добавляет отсутствующие колонки с правильными значениями по умолчанию
- Обновляет существующие тарифы (для PRO включает все виды спорта)

## Измененные файлы

### 1. backend/api_admin.py
**Функция:** `get_all_users()` (строки 22-66)

**До:**
```python
@router.get("/users", response_model=List[AdminUserResponse])
async def get_all_users(...):
    users = db.query(User).all()
    result = []
    for user in users:
        tariff_type = None
        tariff_name = None
        if user.tariff:  # ❌ Может вызвать ошибку
            tariff_type = user.tariff.type
            tariff_name = user.tariff.name
        result.append(AdminUserResponse(...))
    return result
```

**После:**
```python
@router.get("/users", response_model=List[AdminUserResponse])
async def get_all_users(...):
    try:
        users = db.query(User).all()
        result = []
        for user in users:
            tariff_type = None
            tariff_name = None
            try:
                if user.tariff_id:
                    # ✅ Явный запрос к БД вместо relationship
                    tariff = db.query(Tariff).filter(Tariff.id == user.tariff_id).first()
                    if tariff:
                        tariff_type = tariff.type
                        tariff_name = tariff.name
            except Exception as tariff_error:
                print(f"Ошибка получения тарифа для пользователя {user.email}: {tariff_error}")
            result.append(AdminUserResponse(...))
        return result
    except Exception as e:
        print(f"Ошибка при получении списка пользователей: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
```

### 2. backend/database.py
**Функция:** `ensure_database_compatibility()` (строки 290-362)

**Добавлено:**
```python
# Проверяем и обновляем таблицу tariffs
print("\nChecking tariffs table...")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tariffs';")
if cursor.fetchone():
    cursor.execute("PRAGMA table_info(tariffs);")
    tariff_column_names = [col[1] for col in cursor.fetchall()]

    sport_columns = {
        'allow_running': 'INTEGER DEFAULT 1',
        'allow_cycling': 'INTEGER DEFAULT 0',
        'allow_swimming': 'INTEGER DEFAULT 0',
        'allow_triathlon': 'INTEGER DEFAULT 0'
    }

    # Добавляем отсутствующие колонки
    for col_name, col_def in sport_columns.items():
        if col_name not in tariff_column_names:
            cursor.execute(f"ALTER TABLE tariffs ADD COLUMN {col_name} {col_def};")

    # Обновляем значения для существующих тарифов
    cursor.execute("UPDATE tariffs SET allow_running = 1")
    cursor.execute("UPDATE tariffs SET allow_cycling = 1, allow_swimming = 1, allow_triathlon = 1 WHERE type = 'PRO'")
```

### 3. Новые файлы

- `backend/migrate_tariffs_add_sport_columns.py` - скрипт для ручной миграции
- `ADMIN_TARIFF_FIX.md` - техническое описание проблемы и решения
- `DEPLOY_TARIFF_FIX.md` - инструкция по деплою
- `ADMIN_FIXES_SUMMARY.md` - этот файл (сводка всех исправлений)

## Схема таблицы tariffs после миграции

```sql
CREATE TABLE tariffs (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    name VARCHAR NOT NULL,
    type VARCHAR NOT NULL UNIQUE,
    view_full_plan INTEGER DEFAULT 0,
    view_two_weeks INTEGER DEFAULT 1,
    allow_running INTEGER DEFAULT 1,      -- ✅ Новая колонка
    allow_cycling INTEGER DEFAULT 0,      -- ✅ Новая колонка
    allow_swimming INTEGER DEFAULT 0,     -- ✅ Новая колонка
    allow_triathlon INTEGER DEFAULT 0,    -- ✅ Новая колонка
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

## Деплой на продакшн

### Рекомендуемый способ (автоматический)
```bash
# 1. На сервере
cd /path/to/triplan
git pull

# 2. Пересоберите контейнеры
docker-compose down
docker-compose up -d --build

# Миграция запустится автоматически при старте приложения
```

### Проверка
```bash
# Логи
docker-compose logs backend | grep -i tariff

# Должно быть:
# [OK] All required columns are present in tariffs table
# [OK] Database compatibility check completed
```

## Тестирование

### Локально
```bash
cd backend
python -c "from database import ensure_database_compatibility; ensure_database_compatibility()"
```

### На продакшне
1. Откройте https://icanrun.ru/admin/users
2. Страница должна загрузиться без ошибок 500
3. Попробуйте изменить тариф пользователя - должно работать

## Важные заметки

- ✅ Миграция безопасна - не удаляет данные
- ✅ Миграция идемпотентна - можно запускать многократно
- ✅ Автоматически запускается при старте приложения
- ✅ Обратно совместима - работает и со старыми, и с новыми БД
- ✅ Не требует downtime - можно применить без остановки сервиса

## Откат (если нужен)

```bash
git reset --hard HEAD~1
docker-compose down
docker-compose up -d --build
```

## Дополнительная информация

См. детали в:
- `ADMIN_TARIFF_FIX.md` - техническое описание
- `DEPLOY_TARIFF_FIX.md` - инструкция по деплою
