# Исправление проблем админки через API

## Проблема
Файлы скриптов не попали в Docker контейнер, поэтому нельзя запустить `fix_admin_issues.py`.

## Решение через API

### Вариант 1: Через curl
```bash
# Сначала получите токен администратора
TOKEN=$(curl -s -X POST https://icanrun.ru/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "abramov.yu.v@gmail.com", "password": "admin123"}' \
  | jq -r '.access_token')

# Затем вызовите endpoint исправления
curl -X POST https://icanrun.ru/api/v1/admin/fix-issues \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

### Вариант 2: Через браузер (консоль разработчика)
1. Откройте https://icanrun.ru/admin
2. Войдите как администратор
3. Откройте консоль разработчика (F12)
4. Выполните:

```javascript
// Исправить все проблемы админки
fetch('/api/v1/admin/fix-issues', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('token')}`,
    'Content-Type': 'application/json'
  }
})
.then(response => response.json())
.then(data => {
  console.log('Результат исправления:', data);
  if (data.success) {
    console.log('✅ Успешно исправлено!');
    data.details.forEach(detail => console.log(detail));
  } else {
    console.log('❌ Ошибка:', data.message);
  }
});
```

### Вариант 3: Через Postman/Insomnia
1. **POST** `https://icanrun.ru/api/v1/admin/fix-issues`
2. **Headers:**
   - `Authorization: Bearer YOUR_TOKEN`
   - `Content-Type: application/json`
3. **Body:** пустой

## Что делает endpoint

Endpoint `/api/v1/admin/fix-issues` выполняет:

1. ✅ Создает все таблицы, если их нет
2. ✅ Добавляет колонку `tariff_id` в таблицу `users`
3. ✅ Создает тарифы по умолчанию (Тестовый, Пробный, Про)
4. ✅ Назначает тестовый тариф пользователям без тарифа
5. ✅ Создает коэффициенты тренировок по умолчанию
6. ✅ Создает администратора, если его нет
7. ✅ Возвращает подробную статистику

## Ответ API

### Успешный ответ:
```json
{
  "success": true,
  "message": "Все проблемы админки исправлены успешно!",
  "details": [
    "📋 Создание таблиц...",
    "✅ Таблицы проверены/созданы",
    "💳 Исправление тарифов...",
    "✅ Колонка tariff_id уже существует",
    "✅ Тарифы уже существуют",
    "⚙️ Исправление коэффициентов...",
    "✅ Коэффициенты уже существуют",
    "👤 Проверка администратора...",
    "✅ Администратор уже существует",
    "📊 Итоговая статистика:",
    "   • Тарифов: 3",
    "   • Пользователей: 10",
    "   • Коэффициентов: 1",
    "🎉 Все проблемы админки исправлены успешно!"
  ]
}
```

### Ответ с ошибкой:
```json
{
  "success": false,
  "message": "Ошибка при исправлении проблем: ...",
  "details": [...]
}
```

## После исправления

1. ✅ Обновите страницу админки
2. ✅ Проверьте загрузку пользователей
3. ✅ Попробуйте изменить тариф пользователя
4. ✅ Проверьте загрузку коэффициентов тренировок

Все должно работать без ошибок 500! 🎉
