# Система неактивных тарифов и автоматического истечения тестового периода

## Описание

Реализована система автоматического перехода пользователей с тестового тарифа на неактивный тариф через 14 дней после регистрации.

## Основные компоненты

### 1. Новый тип тарифа: INACTIVE

**Файл:** `backend/database.py`

```python
class TariffType(str, enum.Enum):
    TEST = "test"           # Тестовый
    TRIAL = "trial"         # Пробный
    PRO = "pro"             # Про
    INACTIVE = "inactive"   # Неактивный (истекший тестовый период)
```

**Параметры неактивного тарифа:**
- `view_full_plan = 0` - Не может просматривать весь план
- `view_two_weeks = 0` - Не может просматривать даже 2 недели
- Доступны только тренировки до даты истечения тестового периода

### 2. Новое поле в модели User

**Поле:** `test_period_end_date` (DateTime)

Хранит дату окончания тестового периода для автоматического перехода на неактивный тариф.

```python
test_period_end_date = Column(DateTime, nullable=True)
```

**Установка при регистрации:**
```python
# В auth.py, функция create_user
test_period_end = datetime.utcnow() + timedelta(days=14)
user.test_period_end_date = test_period_end
```

### 3. Модуль управления тарифами

**Файл:** `backend/tariff_manager.py`

#### Функция `check_and_update_expired_test_tariff()`
Проверяет и автоматически переводит пользователя на неактивный тариф, если тестовый период истек.

```python
def check_and_update_expired_test_tariff(db: Session, user: User) -> User:
    """Автоматический переход на неактивный тариф"""
    if user.tariff.type == TariffType.TEST:
        if datetime.utcnow() >= user.test_period_end_date:
            inactive_tariff = db.query(Tariff).filter(
                Tariff.type == TariffType.INACTIVE
            ).first()
            user.tariff_id = inactive_tariff.id
            db.commit()
    return user
```

#### Функция `get_test_period_days_remaining()`
Возвращает количество дней до конца тестового периода.

```python
def get_test_period_days_remaining(user: User) -> int | None:
    """Количество дней до конца тестового периода"""
    if user.tariff.type != TariffType.TEST:
        return None
    delta = user.test_period_end_date - datetime.utcnow()
    return max(0, delta.days)
```

### 4. Обновленный API endpoint

**Файл:** `backend/api_user_tariffs.py`

**Endpoint:** `GET /api/v1/user/tariff`

Автоматически проверяет и обновляет тариф при каждом запросе:

```python
@router.get("/tariff", response_model=UserTariffResponse)
async def get_user_tariff(...):
    # Проверка и автоматическое обновление тарифа
    current_user = check_and_update_expired_test_tariff(db, current_user)
    
    # Получение количества дней до конца
    days_remaining = get_test_period_days_remaining(current_user)
    
    return UserTariffResponse(
        tariff_type=current_user.tariff.type,
        tariff_name=current_user.tariff.name,
        test_period_days_remaining=days_remaining,
        test_period_end_date=current_user.test_period_end_date.isoformat()
    )
```

### 5. Обновленная схема ответа

**Файл:** `backend/schemas.py`

```python
class UserTariffResponse(BaseModel):
    tariff_type: Optional[str] = None
    tariff_name: Optional[str] = None
    test_period_days_remaining: Optional[int] = None
    test_period_end_date: Optional[str] = None
```

## Frontend интеграция

### 1. Обновленный тип TypeScript

**Файл:** `frontend/src/types/api.ts`

```typescript
export interface UserTariffResponse {
  tariff_type: string | null;
  tariff_name: string | null;
  test_period_days_remaining: number | null;
  test_period_end_date: string | null;
}
```

### 2. Логика отображения в календаре

**Файл:** `frontend/src/components/calendar.tsx`

```typescript
// Неактивный тариф - доступны только тренировки до даты истечения
if (userTariff.tariff_type === 'inactive') {
  if (userTariff.test_period_end_date) {
    const testPeriodEnd = new Date(userTariff.test_period_end_date);
    return workout < testPeriodEnd;
  }
  return false;
}
```

### 3. Отображение в профиле

**Файл:** `frontend/src/app/profile/page.tsx`

**Для тестового тарифа:**
```tsx
{userTariff?.tariff_type === 'test' && (
  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
    <span>⏰</span>
    <span>
      До конца тестового периода: {userTariff.test_period_days_remaining} дней
    </span>
  </div>
)}
```

**Для неактивного тарифа:**
```tsx
{userTariff?.tariff_type === 'inactive' && (
  <div className="bg-red-50 border border-red-200 rounded-lg p-3">
    <span>⚠️</span>
    <div>
      <div>Тестовый период истек</div>
      <div>Обновите тариф для полного доступа</div>
    </div>
  </div>
)}
```

## Workflow

### Жизненный цикл пользователя

```
День 0: Регистрация
├─→ Создается user
├─→ Назначается тестовый тариф
└─→ test_period_end_date = now + 14 дней

День 1-13: Активный тестовый период
├─→ tariff_type = 'test'
├─→ Доступны тренировки на 14 дней вперед
└─→ Отображается: "До конца: X дней"

День 14: Последний день тестового периода
├─→ tariff_type = 'test'
├─→ Доступны тренировки на текущий день
└─→ Отображается: "До конца: 0 дней"

День 15: Автоматический переход
├─→ При запросе /api/v1/user/tariff:
│   └─→ check_and_update_expired_test_tariff()
│       └─→ tariff_type = 'inactive'
├─→ Доступны только тренировки до дня 14
└─→ Отображается: "Тестовый период истек"

День 16+: Неактивный тариф
├─→ tariff_type = 'inactive'
├─→ Все тренировки после дня 14 замылены
└─→ Призыв к апгрейду тарифа
```

## Правила доступа к тренировкам

| Тариф | Доступ | Замыленные тренировки |
|-------|--------|----------------------|
| **Test** | 14 дней от сегодня | После 14 дней |
| **Inactive** | До даты истечения (test_period_end_date) | После даты истечения |
| **Trial** | 21 день от сегодня | После 21 дня |
| **Pro** | Весь план | Нет |

## Инициализация

### Для новой базы данных:

```bash
python backend/init_admin_data.py
```

Создаст все 4 тарифа:
- Тестовый
- Пробный
- Про
- **Неактивный**

### Для существующей базы данных:

```bash
python backend/add_inactive_tariff.py
```

Добавит неактивный тариф в существующую БД.

## Миграция базы данных

При запуске приложения автоматически добавляется поле `test_period_end_date`:

```python
# В database.py
required_columns = {
    'competition_date': 'DATE',
    'competition_type': 'VARCHAR',
    'tariff_id': 'INTEGER',
    'test_period_end_date': 'DATETIME'  # Новое поле
}
```

## Тестирование

### 1. Создание тестового пользователя

```bash
# Зарегистрируйте пользователя
POST /api/v1/auth/register
{
  "email": "test@example.com",
  "password": "test123"
}
```

### 2. Проверка тарифа

```bash
# Получите информацию о тарифе
GET /api/v1/user/tariff
Authorization: Bearer <token>

# Ответ:
{
  "tariff_type": "test",
  "tariff_name": "Тестовый",
  "test_period_days_remaining": 14,
  "test_period_end_date": "2024-10-30T10:00:00"
}
```

### 3. Симуляция истечения

Для тестирования можно вручную изменить дату в БД:

```sql
UPDATE users 
SET test_period_end_date = datetime('now', '-1 day')
WHERE email = 'test@example.com';
```

Затем запросить `/api/v1/user/tariff` - пользователь автоматически перейдет на неактивный тариф.

## Визуальные примеры

### Профиль: Тестовый тариф (7 дней осталось)

```
┌─────────────────────────────────────┐
│ Тарифный план                       │
│                                     │
│ Текущий тариф: Тестовый            │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ ⏰ До конца тестового периода:  │ │
│ │    7 дней                       │ │
│ └─────────────────────────────────┘ │
│                                     │
│ [Сменить тарифный план]            │
└─────────────────────────────────────┘
```

### Профиль: Неактивный тариф

```
┌─────────────────────────────────────┐
│ Тарифный план                       │
│                                     │
│ Текущий тариф: Неактивный          │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ ⚠️  Тестовый период истек       │ │
│ │    Обновите тариф для полного   │ │
│ │    доступа к тренировкам        │ │
│ └─────────────────────────────────┘ │
│                                     │
│ [Сменить тарифный план]            │
└─────────────────────────────────────┘
```

### Календарь: Неактивный тариф

```
Октябрь 2024 (Истек 30-го)
─────────────────────────────────────
  23   24   25   26   27   28   29
  ✅   ✅   ✅   ✅   ✅   ✅   ✅    ← До 30-го (доступно)

  30   31    1    2    3    4    5
  ✅   🔒   🔒   🔒   🔒   🔒   🔒    ← После 30-го (замылено)
```

## API Endpoints

### GET /api/v1/user/tariff

**Описание:** Получить информацию о тарифе пользователя с автоматической проверкой истечения

**Ответ:**
```json
{
  "tariff_type": "test",
  "tariff_name": "Тестовый",
  "test_period_days_remaining": 7,
  "test_period_end_date": "2024-10-30T12:00:00"
}
```

## Преимущества

✅ **Автоматизация:** Переход на неактивный тариф происходит автоматически  
✅ **Прозрачность:** Пользователь видит количество дней до конца  
✅ **Мотивация:** Четкое уведомление об истечении мотивирует к апгрейду  
✅ **Гибкость:** Можно легко изменить длительность тестового периода  
✅ **Безопасность:** Прошлые тренировки остаются доступными  

## Возможные улучшения

1. **Email уведомления:**
   - За 3 дня до истечения
   - В день истечения
   - Через неделю после истечения

2. **Push уведомления:**
   - Напоминание о приближающемся истечении

3. **Специальные предложения:**
   - Скидка на апгрейд в последний день
   - Бонусы за раннее продление

4. **Аналитика:**
   - Отслеживание конверсии test → pro
   - A/B тестирование длительности тестового периода

## Совместимость

- ✅ SQLite
- ✅ PostgreSQL (требуется изменение типа DATETIME на TIMESTAMP)
- ✅ MySQL
- ✅ Обратная совместимость с существующими пользователями

