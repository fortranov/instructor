#!/bin/bash
# Быстрая проверка силовых тренировок в Docker

echo "======================================================================"
echo "Проверка силовых тренировок (Docker)"
echo "======================================================================"
echo ""

# Проверяем, что контейнер запущен
if ! docker ps | grep -q backend; then
    echo "❌ Контейнер backend не запущен!"
    echo "   Запустите: docker-compose up -d backend"
    exit 1
fi

echo "✅ Контейнер backend запущен"
echo ""

# Проверяем схему базы данных
echo "Проверка схемы базы данных..."
echo "----------------------------------------------------------------------"
docker exec backend python check_database_schema.py /app/data/triplan.db

echo ""
echo "======================================================================"
echo "Дополнительная информация:"
echo "======================================================================"

# Проверяем силовые тренировки
docker exec backend python -c "
import sqlite3
conn = sqlite3.connect('/app/data/triplan.db')
cursor = conn.cursor()

# Пользователи с включенной настройкой
cursor.execute('SELECT COUNT(*) FROM users WHERE has_strength_training = 1')
users_with_strength = cursor.fetchone()[0]
print(f'Пользователей с включенной настройкой: {users_with_strength}')

# Всего силовых тренировок
cursor.execute('SELECT COUNT(*) FROM workouts WHERE LOWER(sport_type) = \"strength\"')
total_strength = cursor.fetchone()[0]
print(f'Всего силовых тренировок в базе: {total_strength}')

# Планы с силовыми тренировками
cursor.execute('''
    SELECT COUNT(DISTINCT p.id)
    FROM training_plans p
    JOIN workouts w ON w.plan_id = p.id
    WHERE LOWER(w.sport_type) = \"strength\"
''')
plans_with_strength = cursor.fetchone()[0]
print(f'Планов с силовыми тренировками: {plans_with_strength}')

conn.close()
"

echo ""
echo "======================================================================"
echo ""
echo "Если нужна миграция:"
echo "  docker exec backend python migrate_add_strength_training.py /app/data/triplan.db"
echo ""
echo "Если нужно пересоздать план:"
echo "  Профиль → Включить силовые тренировки → Изменить план"
echo ""
