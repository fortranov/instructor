# Деплой исправлений для силовых тренировок

## Что исправлено

### 1. Расширены фазы для силовых тренировок
**Файл**: `backend/plan_generator.py:128`
- **Было**: Силовые только в фазах `base` и `build` (>4 недели до соревнования)
- **Стало**: Силовые в фазах `base`, `build` и `peak` (>2 недели до соревнования)

### 2. Улучшена логика добавления силовых
**Файл**: `backend/plan_generator.py:416-503`
- **Было**: Силовая добавляется только в свободный день
- **Стало**: Две стратегии:
  1. Если есть свободный день - добавить туда
  2. Если все дни заняты - добавить в день с минимальной нагрузкой

Это нормально для триатлона - можно делать силовую и другие виды спорта в один день.

## Инструкция по деплою

### На сервере (icanrun.ru)

```bash
# 1. Подключиться к серверу
ssh user@your-server

# 2. Перейти в директорию проекта
cd ~/www/instructor

# 3. Обновить код
git pull origin main

# 4. Пересобрать и перезапустить backend
docker-compose up -d --build backend

# 5. Проверить, что backend запустился
docker-compose ps
docker logs backend --tail 50

# 6. Проверить health endpoint
curl http://localhost:8000/api/v1/health
```

### Проверка результата

1. **Войдите в аккаунт** на icanrun.ru
2. **Перейдите в профиль** (раздел "Настройки")
3. **Убедитесь**, что чекбокс "Включить силовые тренировки в план" установлен
4. **Удалите текущий план** (если есть)
5. **Создайте новый план** с теми же параметрами
6. **Перейдите в раздел "План"**
7. **Проверьте**, что силовые тренировки (🏋️) появились в календаре

### Если силовые всё равно не появляются

#### Вариант 1: Проверить has_strength_training в БД

```bash
docker exec -it backend python << 'EOF'
from database import SessionLocal, User
db = SessionLocal()
user = db.query(User).filter(User.email == "your@email.com").first()
print(f"has_strength_training: {user.has_strength_training}")
if not user.has_strength_training:
    user.has_strength_training = 1
    db.commit()
    print("✅ Исправлено!")
db.close()
EOF
```

#### Вариант 2: Запустить скрипт для добавления силовых в существующие планы

```bash
# Скопировать скрипт
docker cp backend/fix_strength_complete.py backend:/app/fix_strength_complete.py

# Запустить
docker exec -it backend python /app/fix_strength_complete.py
```

## Созданные файлы для диагностики

- `backend/check_strength_workouts.py` - проверка силовых в БД
- `backend/fix_add_strength_workouts.py` - диагностика и добавление силовых
- `backend/add_strength_workouts_force.py` - принудительное добавление силовых
- `backend/fix_strength_complete.py` - комплексное исправление (рекомендуется)

## Технические детали

### Фазы тренировок
- **base**: > 8 недель до соревнования (силовые ✅)
- **build**: 4-8 недель до соревнования (силовые ✅)
- **peak**: 2-4 недели до соревнования (силовые ✅)
- **taper**: < 2 недель до соревнования (силовые ❌)

### Параметры силовой тренировки
- Длительность: 50 минут
- Тип тренировки: RECOVERY
- Частота: 1 раз в неделю

### Логика размещения
1. Ищется свободный предпочтительный день недели
2. Если все дни заняты, силовая добавляется в день с минимальной суммарной продолжительностью тренировок
3. Это позволяет совмещать силовую с бегом/плаванием/велосипедом, что нормально для триатлона

## Логи для отладки

```bash
# Просмотр логов backend
docker logs backend --tail 100 -f

# Проверка работы API
curl http://localhost:8000/api/v1/health

# Проверка силовых в БД напрямую
docker exec -it backend sqlite3 /app/data/triplan.db << 'EOF'
SELECT COUNT(*) FROM workouts WHERE sport_type = 'strength';
.exit
EOF
```
