# Автоматическое назначение тестового тарифа при регистрации

## Описание изменений

При регистрации нового пользователя ему автоматически назначается **тестовый тариф**.

## Внесённые изменения

### 1. Модификация файла `auth.py`

**Строка 15**: Добавлены импорты:
```python
from database import get_db, User, Tariff, TariffType
```

**Строки 81-93**: Обновлена функция `create_user`:
```python
def create_user(db: Session, email: str, password: str, first_name: str = None, last_name: str = None) -> User:
    """Создать нового пользователя"""
    # ... существующий код ...
    
    # Найти тестовый тариф
    test_tariff = db.query(Tariff).filter(Tariff.type == TariffType.TEST).first()
    
    # Создать пользователя
    hashed_password = get_password_hash(password)
    user = User(
        uin=uin,
        email=email,
        hashed_password=hashed_password,
        first_name=first_name,
        last_name=last_name,
        is_active=1,
        tariff_id=test_tariff.id if test_tariff else None  # Назначение тестового тарифа
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
```

## Тестирование

### Автоматический тест

Создан тестовый скрипт `test_tariff_assignment.py`, который проверяет:
1. Наличие тестового тарифа в базе данных
2. Автоматическое назначение тарифа при регистрации
3. Корректность назначенного тарифа

**Запуск теста:**
```bash
python backend/test_tariff_assignment.py
```

**Результат теста:**
```
✅ ТЕСТ ПРОЙДЕН: Тестовый тариф назначен автоматически!

Информация о тарифе:
  • Просмотр всего плана: Нет
  • Просмотр двух недель: Да
```

## Параметры тестового тарифа

| Параметр | Значение |
|----------|----------|
| Название | Тестовый |
| Тип | `test` |
| Просмотр всего плана | Нет |
| Просмотр двух недель | Да |

## API Endpoints

### POST `/api/v1/auth/register`
При регистрации через этот endpoint новому пользователю автоматически назначается тестовый тариф.

**Пример запроса:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "first_name": "Иван",
  "last_name": "Иванов"
}
```

**Пример ответа:**
```json
{
  "id": 1,
  "uin": "unique-identifier",
  "email": "user@example.com",
  "first_name": "Иван",
  "last_name": "Иванов",
  "is_active": true,
  "preferred_workout_days": [0,1,2,3,4,5,6],
  "created_at": "2024-10-16T10:00:00"
}
```

### GET `/api/v1/user/tariff`
Получить информацию о текущем тарифе пользователя.

**Заголовки:**
```
Authorization: Bearer <token>
```

**Пример ответа:**
```json
{
  "tariff_type": "test",
  "tariff_name": "Тестовый"
}
```

## Примечания

- Если тестовый тариф не найден в базе данных, полю `tariff_id` будет присвоено значение `None`
- Для корректной работы необходимо, чтобы в базе данных существовал тариф с типом `TariffType.TEST`
- Инициализация тарифов производится скриптом `init_admin_data.py`

## Инициализация базы данных

Для создания тестового тарифа в базе данных выполните:

```bash
python backend/init_admin_data.py
```

Этот скрипт создаст:
- Тестовый тариф
- Пробный тариф  
- Про тариф
- Коэффициенты тренировок
- Пользователя-администратора

