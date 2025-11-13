# Силовые тренировки не отображаются - Устранение проблемы

## Быстрая диагностика

### Шаг 1: Проверьте конкретного пользователя

```bash
# Локально
cd backend
python check_user_strength_workouts.py user@email.com

# В Docker
docker exec backend python check_user_strength_workouts.py user@email.com /app/data/triplan.db
```

---

## Частые причины и решения

### ❌ Проблема 1: has_strength_training = OFF

**Диагностика:**
```
has_strength_training: OFF
```

**Решение:**
1. Войти в **Профиль**
2. Включить **"Включить силовые тренировки в план"** ✅
3. Нажать **"Изменить план тренировок"**

---

### ❌ Проблема 2: План создан ДО включения настройки

**Диагностика:**
```
[!] PROBLEMA: Plan sozdan DO vklyucheniya nastrojki!
Plan sozdan: 2025-11-01 10:00:00
Nastrojka vklyuchena: 2025-11-04 14:00:00
```

**Решение:**
1. Войти в **Профиль**
2. Нажать **"Изменить план тренировок"**
3. План будет пересоздан с силовыми тренировками

⚠️ **Важно:** План НЕ обновляется автоматически!

---

### ❌ Проблема 3: До соревнования меньше 8 недель

**Диагностика:**
```
Nedel' do sorevnovaniya: 4
PRICHINA: Do sorevnovaniya men'she 8 nedel'
```

**Объяснение:**
Силовые тренировки добавляются только в фазах **base** и **build** (первые ~8 недель).

**Решение:**
Это нормальное поведение. Если нужны силовые на всех фазах, измените логику в `backend/plan_generator.py:127`.

---

### ❌ Проблема 4: Поле has_strength_training отсутствует в БД

**Диагностика:**
```
[MISSING] has_strength_training - OTSUTSTVUET!
```

**Решение:**
Нужна миграция базы данных:

```bash
# Docker
docker exec backend cp /app/data/triplan.db /app/data/triplan.db.backup.$(date +%Y%m%d_%H%M%S)
docker exec backend python migrate_add_strength_training.py /app/data/triplan.db
docker-compose restart backend

# Без Docker
cp triplan.db triplan.db.backup.$(date +%Y%m%d_%H%M%S)
python migrate_add_strength_training.py ./triplan.db
systemctl restart triplan-backend
```

---

## Проверка на frontend

Если силовые есть в базе, но не отображаются в браузере:

### 1. Очистите кеш браузера

**Chrome/Edge:**
- Нажмите `Ctrl+Shift+Delete`
- Выберите "Кешированные изображения и файлы"
- Нажмите "Удалить данные"

**Firefox:**
- Нажмите `Ctrl+Shift+Delete`
- Выберите "Кеш"
- Нажмите "Удалить сейчас"

### 2. Проверьте в консоли браузера

Откройте консоль (`F12`) и выполните:

```javascript
// Проверка текущих тренировок
console.log('Workouts:', window.location.pathname);

// Обновите страницу с очисткой кеша
location.reload(true);
```

### 3. Проверьте Network запросы

1. Откройте DevTools (`F12`)
2. Перейдите на вкладку **Network**
3. Обновите страницу
4. Найдите запрос к `/api/v1/plans/.../workouts`
5. Проверьте Response - есть ли в нём `"sport_type": "strength"`?

Если есть → проблема в отображении
Если нет → проблема в backend/database

---

## Команды для быстрой диагностики (Docker)

```bash
# 1. Проверка базы данных
docker exec backend python check_database_schema.py /app/data/triplan.db

# 2. Проверка конкретного пользователя
docker exec backend python check_user_strength_workouts.py user@email.com /app/data/triplan.db

# 3. Проверка всех силовых тренировок
docker exec backend python -c "
import sqlite3
conn = sqlite3.connect('/app/data/triplan.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM workouts WHERE LOWER(sport_type) = \"strength\"')
print(f'Silovyh trenirovok v baze: {cursor.fetchone()[0]}')
conn.close()
"

# 4. Проверка логов backend
docker-compose logs -f backend | grep -i strength
```

---

## Контрольный список

- [ ] Миграция выполнена (`has_strength_training` существует)
- [ ] Пользователь включил настройку (has_strength_training = 1)
- [ ] План пересоздан ПОСЛЕ включения настройки
- [ ] До соревнования больше 8 недель
- [ ] В базе есть силовые тренировки (sport_type = 'strength')
- [ ] API возвращает силовые тренировки
- [ ] Кеш браузера очищен
- [ ] Силовые отображаются в плане ✅

---

## Скрипты для диагностики

- `check_database_schema.py` - проверка схемы БД
- `check_user_strength_workouts.py` - проверка конкретного пользователя
- `check_strength_docker.sh` - общая диагностика Docker

---

## Если ничего не помогло

1. Проверьте логи backend:
   ```bash
   docker-compose logs -f backend
   ```

2. Создайте новый тестовый план:
   - Зарегистрируйте нового пользователя
   - Включите силовые тренировки
   - Создайте план
   - Проверьте, отображаются ли силовые

3. Проверьте версию кода:
   ```bash
   git log --oneline -5
   ```

4. Обратитесь к документации:
   - `STRENGTH_TRAINING_README.md`
   - `DOCKER_STRENGTH_TRAINING_FIX.md`

---

**Дата:** 4 ноября 2025
