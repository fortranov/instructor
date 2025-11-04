# Инструкция: Исправление силовых тренировок на продакшене

## Проблема

Силовые тренировки не отображаются в планах пользователей.

## Возможные причины

1. **База данных не имеет поля `has_strength_training`** (требуется миграция)
2. **У пользователей настройка `has_strength_training = 0`** (выключено)
3. **План был создан ДО включения настройки** (нужно пересоздать план)

---

## Шаг 1: Проверка базы данных на продакшене

Загрузите файл `backend/check_database_schema.py` на продакшен-сервер и выполните:

```bash
cd /path/to/triplan/backend
python check_database_schema.py ./triplan.db
```

### Ожидаемый вывод (если всё ОК):

```
[SUCCESS] BAZA DANNYH GOTOVA K RABOTE

Vse neobhodimye polya prisutstvuyut.
```

### Если увидели ошибку:

```
[MISSING] has_strength_training - OTSUTSTVUET!
[WARNING] TREBUETSYA MIGRACIYA!
```

**→ Переходите к Шагу 2**

---

## Шаг 2: Миграция базы данных (если нужна)

### 2.1. Создайте backup

```bash
cd /path/to/triplan/backend
cp triplan.db triplan.db.backup.$(date +%Y%m%d_%H%M%S)
```

### 2.2. Примените миграцию

**Вариант A: Через Python скрипт**

```bash
python migrate_add_strength_training.py ./triplan.db
```

**Вариант B: Прямой SQL**

```bash
sqlite3 triplan.db "ALTER TABLE users ADD COLUMN has_strength_training INTEGER DEFAULT 0;"
```

### 2.3. Перезапустите backend

**Для systemd:**
```bash
sudo systemctl restart triplan-backend
sudo systemctl status triplan-backend
```

**Для PM2:**
```bash
pm2 restart triplan-backend
pm2 logs triplan-backend
```

**Для Docker:**
```bash
docker-compose restart backend
docker-compose logs -f backend
```

---

## Шаг 3: Включение силовых тренировок для пользователей

После миграции пользователям нужно:

1. Войти в **Профиль**
2. Включить опцию **"Включить силовые тренировки в план"** ✅
3. Нажать кнопку **"Изменить план тренировок"** (или **"Создать план тренировок"**)

**ВАЖНО:** План не обновляется автоматически! Нужно **пересоздать** план после включения настройки.

---

## Шаг 4: Проверка работы

### 4.1. Проверьте настройку пользователя

```bash
cd /path/to/triplan/backend
python -c "
import sqlite3
conn = sqlite3.connect('./triplan.db')
cursor = conn.cursor()
cursor.execute('SELECT email, has_strength_training FROM users')
for row in cursor.fetchall():
    print(f'{row[0]}: {\"ON\" if row[1] == 1 else \"OFF\"}')
conn.close()
"
```

### 4.2. Проверьте наличие силовых тренировок в плане

```bash
python -c "
import sqlite3
conn = sqlite3.connect('./triplan.db')
cursor = conn.cursor()

# Найдите пользователя с включенной настройкой
cursor.execute('''
    SELECT u.email, COUNT(w.id) as strength_count
    FROM users u
    LEFT JOIN training_plans p ON p.user_id = u.id
    LEFT JOIN workouts w ON w.plan_id = p.id AND LOWER(w.sport_type) = \"strength\"
    WHERE u.has_strength_training = 1
    GROUP BY u.id
''')

print('Пользователи с включенными силовыми тренировками:')
for row in cursor.fetchall():
    print(f'  {row[0]}: {row[1]} силовых тренировок')

conn.close()
"
```

Ожидаемый результат: **9 силовых тренировок** для 12-недельного плана

---

## Частые вопросы

### Q: Почему силовые тренировки не появляются после включения настройки?

**A:** План не обновляется автоматически. Нужно **пересоздать план** через кнопку "Изменить план тренировок" в профиле.

### Q: Сколько силовых тренировок должно быть в плане?

**A:**
- ~1 силовая тренировка в неделю
- Только в фазах **base** и **build** (первые ~8 недель)
- Для 12-недельного плана: **~9 силовых тренировок**
- Длительность: **50 минут**

### Q: Как откатить изменения, если что-то пошло не так?

**A:**

```bash
cd /path/to/triplan/backend

# Остановите backend
sudo systemctl stop triplan-backend  # или pm2 stop / docker-compose stop

# Восстановите backup
cp triplan.db.backup.XXXXXXXX_XXXXXX triplan.db

# Запустите backend
sudo systemctl start triplan-backend  # или pm2 start / docker-compose start
```

---

## Технические детали

### Где добавляются силовые тренировки

- **Файл:** `backend/plan_generator.py:126-132`
- **Условия:**
  - `user.has_strength_training = 1`
  - Фаза тренировки: `base` или `build`
  - 1 силовая тренировка в неделю
  - Размещается в свободный предпочтительный день

### Структура базы данных

```sql
-- Таблица users должна иметь поле:
has_strength_training INTEGER DEFAULT 0

-- Тренировки с типом:
sport_type = 'STRENGTH'  -- или 'strength'
```

---

## Контрольный чеклист

- [ ] Создан backup базы данных
- [ ] Выполнена проверка схемы (`check_database_schema.py`)
- [ ] Применена миграция (если требовалась)
- [ ] Backend перезапущен
- [ ] Пользователи включили настройку в профиле
- [ ] Планы пересозданы
- [ ] Силовые тренировки появились в планах

---

**Дата:** 4 ноября 2025
