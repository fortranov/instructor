# Исправление проблемы с силовыми тренировками

## Проблема
Силовые тренировки не отображаются в календаре, хотя в настройках плана галочка стоит.

## Причины
1. Силовые тренировки генерировались только в фазах `base` и `build` (>4 недель до соревнования)
2. Возможно, поле `has_strength_training` в БД установлено неправильно (0 вместо 1)

## Исправления в коде
Файл `backend/plan_generator.py:128` - теперь силовые добавляются также в фазе `peak`:
```python
if has_strength_training and phase in ['base', 'build', 'peak']:
```

## Запуск на продакшене (icanrun.ru)

### Шаг 1: Обновить код на сервере

```bash
# Подключиться к серверу через SSH
ssh user@your-server

# Перейти в директорию проекта
cd /path/to/triplan

# Обновить код
git pull origin main

# Перезапустить backend контейнер
docker-compose restart backend

# Проверить, что контейнер запустился
docker-compose ps
```

### Шаг 2: Запустить скрипт исправления

```bash
# Скопировать скрипт в контейнер
docker cp backend/fix_strength_complete.py backend:/app/fix_strength_complete.py

# Запустить скрипт
docker exec -it backend python /app/fix_strength_complete.py

# Скрипт выполнит:
# 1. Установит has_strength_training=1 для пользователей с планами триатлона
# 2. Добавит силовые тренировки в существующие планы (даже в занятые дни)
# 3. Покажет подробную информацию о процессе
```

### Шаг 3: Проверить результат

После запуска скрипта:
1. Обновите страницу с планом в браузере (Ctrl+F5)
2. Силовые тренировки должны появиться в календаре с иконкой 🏋️

## Если проблема остается

### Проверить has_strength_training вручную

```bash
# Подключиться к контейнеру
docker exec -it backend bash

# Запустить Python
python

# В Python консоли:
from database import SessionLocal, User
db = SessionLocal()

# Найти вашего пользователя (замените на ваш email)
user = db.query(User).filter(User.email == "your@email.com").first()

# Проверить значение
print(f"has_strength_training: {user.has_strength_training}")
print(f"has_strength_training (bool): {bool(user.has_strength_training)}")

# Если значение 0, установить 1
if not user.has_strength_training:
    user.has_strength_training = 1
    db.commit()
    print("✅ Исправлено!")

db.close()
exit()
```

### Альтернатива: Создать новый план

Если скрипт не помог:
1. Удалите текущий план (кнопка в интерфейсе)
2. Создайте новый план с теми же параметрами
3. Убедитесь, что галочка "Силовые тренировки" установлена
4. Силовые должны появиться автоматически

## Проверка в БД напрямую

```bash
# Подключиться к SQLite БД
docker exec -it backend sqlite3 /app/data/triplan.db

# Проверить пользователей
SELECT email, has_strength_training FROM users;

# Проверить силовые тренировки
SELECT COUNT(*) FROM workouts WHERE sport_type = 'strength';

# Проверить тренировки конкретного пользователя
SELECT w.date, w.sport_type, w.duration_minutes
FROM workouts w
JOIN training_plans p ON w.plan_id = p.id
JOIN users u ON p.user_id = u.id
WHERE u.email = 'your@email.com'
AND w.sport_type = 'strength';

# Выход
.exit
```

## Логи для отладки

```bash
# Просмотр логов backend
docker logs backend --tail 100 -f

# Проверить health endpoint
curl http://localhost:8000/api/v1/health
```
