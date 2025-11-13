# СРОЧНАЯ ДИАГНОСТИКА: Силовые не отображаются после пересоздания плана

## ШАГ 1: Проверьте, что силовые есть в базе данных

```bash
# В Docker
docker exec backend python check_user_strength_workouts.py ВАШ@EMAIL.COM /app/data/triplan.db
```

Ожидаемый результат:
```
[SUCCESS] Silovye trenirovki prisutstvuyut v plane!
```

Если видите `Silovyh: 0` → переходите к Решению A
Если видите `Silovyh: 9` → переходите к ШАГ 2

---

## ШАГ 2: Проверьте API напрямую

```bash
# Проверьте, что API возвращает силовые тренировки
docker exec backend python -c "
from database import SessionLocal
from plan_generator import PlanGenerator
from datetime import date, timedelta

db = SessionLocal()
generator = PlanGenerator(db)

# ЗАМЕНИТЕ на свой email
workouts = generator.get_workouts_by_date_range('ВАШ@EMAIL.COM', date.today(), date.today() + timedelta(days=30))

strength_count = sum(1 for w in workouts if w['sport_type'].value.lower() == 'strength')
print(f'API vozvrashhaet silovyh trenirovok: {strength_count}')

db.close()
"
```

Ожидаемый результат: `API vozvrashhaet silovyh trenirovok: X` (где X > 0)

Если `0` → переходите к Решению B
Если `> 0` → переходите к ШАГ 3

---

## ШАГ 3: Проверьте frontend в браузере

### 3.1. Откройте DevTools (F12)

### 3.2. Перейдите на вкладку Network

### 3.3. Обновите страницу с планом

### 3.4. Найдите запрос к API

Найдите запрос вида:
```
GET /api/v1/plans/ВАШ_UIN/workouts?start_date=...&end_date=...
```

### 3.5. Проверьте Response

Нажмите на этот запрос → вкладка **Response**

Найдите в ответе строки с:
```json
{
  "sport_type": "strength",
  ...
}
```

**Если есть** → переходите к ШАГ 4
**Если нет** → переходите к Решению C

---

## ШАГ 4: Очистите кеш и проверьте отображение

### 4.1. Полная очистка кеша

**Метод 1: Hard Refresh**
- `Ctrl + Shift + R` (Chrome/Edge/Firefox)
- `Cmd + Shift + R` (Mac)

**Метод 2: Очистка через DevTools**
1. Откройте DevTools (F12)
2. Правый клик на кнопке обновления страницы
3. Выберите "Очистить кеш и жесткая перезагрузка"

**Метод 3: Полная очистка**
- `Ctrl + Shift + Delete`
- Выберите "Кешированные изображения и файлы"
- Период: "За всё время"
- Нажмите "Удалить данные"

### 4.2. Проверьте снова

Перейдите на страницу плана и проверьте наличие силовых тренировок.

**Если появились** → ✅ РЕШЕНО! Была проблема с кешем.
**Если не появились** → переходите к ШАГ 5

---

## ШАГ 5: Проверьте версию frontend

### 5.1. Проверьте, собран ли новый frontend

```bash
# Проверьте дату последней сборки frontend
docker exec frontend ls -la /app/.next/static/

# Или проверьте логи сборки
docker-compose logs frontend | grep -i "build"
```

### 5.2. Пересоберите frontend

```bash
# Остановите контейнеры
docker-compose stop

# Пересоберите frontend
docker-compose build frontend

# Запустите заново
docker-compose up -d

# Проверьте логи
docker-compose logs -f frontend
```

### 5.3. Проверьте снова

Очистите кеш браузера и проверьте отображение силовых.

---

## РЕШЕНИЕ A: Силовых нет в базе данных

```bash
# 1. Проверьте настройку пользователя
docker exec backend python -c "
import sqlite3
conn = sqlite3.connect('/app/data/triplan.db')
cursor = conn.cursor()
cursor.execute('SELECT email, has_strength_training FROM users WHERE email = \"ВАШ@EMAIL.COM\"')
print(cursor.fetchone())
conn.close()
"

# 2. Если has_strength_training = 0, включите в профиле и пересоздайте план

# 3. Если has_strength_training = 1, проверьте недели до соревнования
docker exec backend python -c "
import sqlite3
from datetime import date
conn = sqlite3.connect('/app/data/triplan.db')
cursor = conn.cursor()
cursor.execute('''
    SELECT p.competition_date
    FROM training_plans p
    JOIN users u ON u.id = p.user_id
    WHERE u.email = \"ВАШ@EMAIL.COM\"
''')
comp_date = cursor.fetchone()[0]
weeks = (date.fromisoformat(comp_date) - date.today()).days // 7
print(f'Nedel\' do sorevnovaniya: {weeks}')
if weeks < 8:
    print('PRICHINA: Men\'she 8 nedel\' - silovye dobavlyayutsya tol\'ko v base/build')
conn.close()
"
```

---

## РЕШЕНИЕ B: API не возвращает силовые

```bash
# Перезапустите backend
docker-compose restart backend

# Проверьте логи
docker-compose logs -f backend | grep -i error

# Проверьте снова API
docker exec backend python check_user_strength_workouts.py ВАШ@EMAIL.COM /app/data/triplan.db
```

---

## РЕШЕНИЕ C: Frontend не получает данные

```bash
# 1. Проверьте логи backend при запросе
docker-compose logs -f backend

# 2. Откройте страницу плана в браузере

# 3. Посмотрите в логи - должен быть запрос GET /api/v1/plans/.../workouts

# 4. Если запроса нет - проблема в frontend

# 5. Пересоберите и перезапустите
docker-compose build frontend backend
docker-compose up -d
```

---

## Быстрый тест: Создайте нового пользователя

Самый надежный способ проверить:

1. Зарегистрируйте нового тестового пользователя
2. Включите силовые тренировки в профиле
3. Создайте план (соревнование через 12+ недель)
4. Проверьте, отображаются ли силовые

**Если у нового пользователя силовые отображаются:**
→ Проблема в конкретном аккаунте (пересоздайте план)

**Если у нового пользователя силовые НЕ отображаются:**
→ Проблема в коде/конфигурации

---

## Проверка кода на продакшене

```bash
# Проверьте версию кода
docker exec backend python -c "
import os
print('Backend code:')
os.system('git log --oneline -1')
"

# Проверьте наличие SportType.STRENGTH
docker exec backend python -c "
from database import SportType
print('SportType.STRENGTH:', SportType.STRENGTH.value)
"

# Проверьте наличие силовых в enum
docker exec backend grep -r "STRENGTH" database.py
```

---

## Если ничего не помогает

### Включите подробное логирование

1. Отредактируйте `backend/plan_generator.py`, добавьте в метод `_generate_workouts()`:

```python
# После строки 132
if strength_workout:
    print(f"DEBUG: Adding strength workout on {strength_workout['date']}")
    workouts.append(strength_workout)
```

2. Пересоберите и проверьте логи:

```bash
docker-compose build backend
docker-compose restart backend

# Пересоздайте план в UI

# Проверьте логи
docker-compose logs backend | grep "DEBUG: Adding strength"
```

---

**ВАЖНО:** Напишите результат каждого шага, чтобы понять, где именно проблема!
