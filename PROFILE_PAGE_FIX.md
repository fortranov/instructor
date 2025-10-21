# Исправление ошибки "B.cycling is not iterable" на странице профиля

## Проблема

При открытии страницы Профиль возникала ошибка:
```
Uncaught TypeError: B.cycling is not iterable
```

## Причина

API эндпоинт `/api/v1/competition-types` возвращает объект `CompetitionTypesResponse` с разными полями в зависимости от тарифа пользователя:

```typescript
// Например, для пользователя с тестовым тарифом
{
  "running": [...],
  // cycling, swimming, triathlon отсутствуют
}
```

Но TypeScript интерфейс определял все поля как обязательные массивы:
```typescript
export interface CompetitionTypesResponse {
  running: CompetitionTypeOption[];
  cycling: CompetitionTypeOption[];  // ❌ Ожидаем массив, получаем undefined
  swimming: CompetitionTypeOption[];
  triathlon: CompetitionTypeOption[];
}
```

Когда код пытался использовать spread оператор на `undefined`:
```typescript
[...competitionTypes.running, ...competitionTypes.cycling, ...]
// ❌ Ошибка: cycling is undefined, не iterable
```

## Исправление

### 1. Обновлен TypeScript интерфейс

**Файл:** `frontend/src/types/api.ts:110-115`

```typescript
export interface CompetitionTypesResponse {
  running?: CompetitionTypeOption[];   // ✅ Опциональные поля
  cycling?: CompetitionTypeOption[];
  swimming?: CompetitionTypeOption[];
  triathlon?: CompetitionTypeOption[];
}
```

### 2. Исправлен код на странице профиля

**Файл:** `frontend/src/app/profile/page.tsx`

#### Место 1: Отображение типа соревнования (строки 510-520)

**До:**
```typescript
[...competitionTypes.running, ...competitionTypes.cycling, ...]
  .find(type => type.value === existingPlan.competition_type)?.label
```

**После:**
```typescript
[
  ...(competitionTypes.running || []),
  ...(competitionTypes.cycling || []),
  ...(competitionTypes.swimming || []),
  ...(competitionTypes.triathlon || [])
]
  .find(type => type.value === existingPlan.competition_type)?.label
```

#### Место 2: Выпадающий список типов соревнований (строки 664-703)

**До:**
```typescript
<optgroup label="Бег">
  {competitionTypes.running.map(type => ...)}  {/* ❌ Может быть undefined */}
</optgroup>
```

**После:**
```typescript
{competitionTypes.running && competitionTypes.running.length > 0 && (
  <optgroup label="Бег">
    {competitionTypes.running.map(type => ...)}  {/* ✅ Проверка наличия */}
  </optgroup>
)}
```

## Что было изменено

### Измененные файлы:

1. **frontend/src/types/api.ts** (строки 110-115)
   - Все поля интерфейса `CompetitionTypesResponse` стали опциональными

2. **frontend/src/app/profile/page.tsx** (строки 510-520, 664-703)
   - Добавлена проверка на `undefined` перед использованием spread оператора
   - Добавлены условные проверки перед рендерингом optgroup элементов

## Логика работы

Теперь код корректно обрабатывает случаи, когда:
- У пользователя тестовый тариф → доступен только бег
- У пользователя триал тариф → доступны бег и другие виды
- У пользователя PRO тариф → доступны все виды спорта

API возвращает только те виды спорта, которые доступны по тарифу, а фронтенд безопасно обрабатывает отсутствующие поля.

## Связанные изменения

Эта ошибка связана с недавними изменениями в тарифной системе:
- Добавлены колонки `allow_running`, `allow_cycling`, `allow_swimming`, `allow_triathlon` в таблицу `tariffs`
- API теперь фильтрует типы соревнований по тарифу пользователя
- См. также: `ADMIN_TARIFF_FIX.md`

## Тестирование

Проверьте, что:
1. Страница профиля загружается без ошибок
2. Для пользователей с разными тарифами отображаются правильные виды спорта
3. Выпадающий список типов соревнований показывает только доступные опции
4. Существующий план отображается с корректным названием типа соревнования

## Деплой

Изменения только во фронтенде:
```bash
cd frontend
npm run build
# Или через Docker
docker-compose down frontend
docker-compose up -d --build frontend
```
