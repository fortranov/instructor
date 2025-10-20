# Развертывание Triplan на продакшене

## Подготовка базы данных

### ✅ Автоматическая инициализация

При развертывании на продакшене база данных создается автоматически со всеми необходимыми колонками и таблицами.

### 🔧 Что создается автоматически:

1. **Все таблицы с правильной структурой:**
   - `users` (включая колонку `tariff_id`)
   - `training_plans`
   - `workouts`
   - `workout_completion_marks`
   - `tariffs` (новая таблица для тарифных планов)
   - `workout_coefficients` (новая таблица для коэффициентов)

2. **Тарифные планы по умолчанию:**
   - **Тестовый**: Просмотр только 2 недель
   - **Пробный**: Просмотр только 2 недель
   - **Про**: Просмотр всего плана

3. **Коэффициенты тренировок по умолчанию**

4. **Пользователь-администратор:**
   - Email: `abramov.yu.v@gmail.com`
   - Пароль: `admin123`

## Инструкции по развертыванию

### 1. Автоматическая инициализация (рекомендуется)

База данных инициализируется автоматически при первом запуске приложения благодаря функциям в `main.py`:

```python
# В main.py автоматически выполняется:
ensure_database_compatibility()  # Проверка и миграция БД
create_tables()                  # Создание таблиц
```

### 2. Ручная инициализация (если нужно)

Если требуется ручная инициализация, выполните:

```bash
cd backend
python init_production_db.py
```

Этот скрипт:
- ✅ Создает все таблицы
- ✅ Добавляет тарифные планы
- ✅ Создает коэффициенты тренировок
- ✅ Создает пользователя-администратора

### 3. Проверка корректности базы данных

Для проверки того, что база данных создана правильно:

```bash
cd backend
python test_production_db.py
```

## Структура базы данных

### Таблица `users`
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    uin VARCHAR UNIQUE NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    first_name VARCHAR,
    last_name VARCHAR,
    is_active INTEGER DEFAULT 1,
    preferred_workout_days VARCHAR DEFAULT '[0,1,2,3,4,5,6]',
    competition_date DATE,
    competition_type VARCHAR,
    tariff_id INTEGER,  -- ✅ Новая колонка для связи с тарифами
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tariff_id) REFERENCES tariffs(id)
);
```

### Таблица `tariffs` (новая)
```sql
CREATE TABLE tariffs (
    id INTEGER PRIMARY KEY,
    name VARCHAR NOT NULL,
    type VARCHAR UNIQUE NOT NULL,
    view_full_plan INTEGER DEFAULT 0,
    view_two_weeks INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Таблица `workout_coefficients` (новая)
```sql
CREATE TABLE workout_coefficients (
    id INTEGER PRIMARY KEY,
    weekly_distance_beginner INTEGER DEFAULT 10,
    weekly_distance_5_10 INTEGER DEFAULT 50,
    -- ... все коэффициенты для расчета планов
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## Переменные окружения

### Обязательные переменные:
```bash
# Путь к базе данных (опционально)
DB_PATH=./triplan.db

# Секретный ключ для JWT (обязательно в продакшене!)
SECRET_KEY=your-super-secret-key-change-in-production
```

### Рекомендуемые настройки для продакшена:
```bash
# Безопасность
SECRET_KEY=your-very-long-random-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24 часа

# База данных
DB_PATH=/app/data/triplan.db
```

## Проверка развертывания

### 1. Проверка API
```bash
curl http://your-domain/api/v1/health
```

### 2. Проверка администратора
```bash
curl -X POST http://your-domain/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "abramov.yu.v@gmail.com", "password": "admin123"}'
```

### 3. Проверка админской панели
Перейдите на `http://your-domain/admin` и войдите как администратор.

## Безопасность

### ⚠️ ВАЖНО: После развертывания

1. **Смените пароль администратора:**
   - Войдите как `abramov.yu.v@gmail.com` / `admin123`
   - Перейдите в профиль
   - Смените пароль на безопасный

2. **Установите надежный SECRET_KEY:**
   ```bash
   export SECRET_KEY="your-very-long-random-secret-key-here"
   ```

3. **Настройте CORS для продакшена:**
   В `main.py` замените:
   ```python
   allow_origins=["*"]  # Только для разработки!
   ```
   На:
   ```python
   allow_origins=["https://your-domain.com"]  # Ваш домен
   ```

## Миграции

### Автоматические миграции
Система автоматически проверяет и добавляет недостающие колонки при запуске через функцию `ensure_database_compatibility()`.

### Ручные миграции
Если нужно выполнить миграцию вручную:
```bash
cd backend
python migrate_admin_tables.py
```

## Мониторинг

### Логи приложения
Приложение выводит подробные логи о состоянии базы данных:
```
Database path: /app/data/triplan.db
Current columns in users table: ['id', 'uin', 'email', ..., 'tariff_id']
✅ All required columns are present
✅ Database compatibility check completed
```

### Проверка состояния
- Все таблицы должны быть созданы
- Колонка `tariff_id` должна присутствовать в таблице `users`
- Должны существовать 3 тарифа по умолчанию
- Должен существовать пользователь `abramov.yu.v@gmail.com`

## Резервное копирование

### Создание бэкапа
```bash
cp /path/to/triplan.db /path/to/backup/triplan_$(date +%Y%m%d_%H%M%S).db
```

### Восстановление
```bash
cp /path/to/backup/triplan_backup.db /path/to/triplan.db
```

## Устранение неполадок

### Ошибка "no such column: users.tariff_id"
Если возникает эта ошибка:
1. Остановите приложение
2. Выполните: `python migrate_admin_tables.py`
3. Перезапустите приложение

### Отсутствуют тарифы
```bash
python init_production_db.py
```

### Отсутствует администратор
```bash
python init_admin_data.py
```
