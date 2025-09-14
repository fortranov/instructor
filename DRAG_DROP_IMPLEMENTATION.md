# Реализация Drag and Drop для календаря тренировок

## Обзор

Добавлена функциональность перетаскивания тренировок в календаре с сохранением новой даты в базе данных.

## Изменения в Backend

### 1. Новая схема данных (`backend/schemas.py`)

```python
class WorkoutDateUpdate(BaseModel):
    workout_id: int = Field(..., description="ID тренировки")
    new_date: date = Field(..., description="Новая дата тренировки")
```

### 2. Новый метод в PlanGenerator (`backend/plan_generator.py`)

```python
def update_workout_date(self, uin: str, workout_id: int, new_date: date) -> bool:
    """Обновить дату тренировки"""
```

### 3. Новый API endpoint (`backend/api_routes.py`)

```
PUT /api/v1/plans/{uin}/workouts/update-date
```

## Изменения в Frontend

### 1. Новые зависимости

```bash
npm install @dnd-kit/core @dnd-kit/utilities
```

### 2. Обновленный тип API (`frontend/src/types/api.ts`)

```typescript
interface WorkoutDateUpdate {
  workout_id: number;
  new_date: string; // ISO date string (YYYY-MM-DD)
}
```

### 3. Новый метод API клиента (`frontend/src/lib/api.ts`)

```typescript
async updateWorkoutDate(uin: string, workoutUpdate: WorkoutDateUpdate)
```

### 4. Обновленный календарь (`frontend/src/components/calendar.tsx`)

- Добавлены компоненты `DraggableWorkout` и `DroppableDay`
- Интеграция с `@dnd-kit/core`
- Обработчики `handleDragStart` и `handleDragEnd`
- Визуальная обратная связь при перетаскивании

### 5. Обновленная страница плана (`frontend/src/app/plan/page.tsx`)

- Добавлен обработчик `handleWorkoutMove`
- Передача обработчика в компонент Calendar
- Обновление локального состояния после успешного перемещения

## Функциональность

### Пользовательский интерфейс

1. **Перетаскивание**: Тренировки можно захватить и перетащить на другой день
2. **Визуальная обратная связь**: 
   - Полупрозрачность при перетаскивании
   - Подсветка дропзоны при наведении
   - DragOverlay с копией перетаскиваемого элемента
3. **Подсказка**: Информационное сообщение о возможности перетаскивания

### Backend логика

1. **Валидация**: Проверка принадлежности тренировки пользователю
2. **Безопасность**: Обновление только тренировок из плана пользователя
3. **Атомарность**: Транзакционное обновление в базе данных

### Обработка ошибок

1. **Frontend**: Обработка ошибок API с выбросом исключений
2. **Backend**: HTTP статус коды и детальные сообщения об ошибках
3. **Откат**: При ошибке локальное состояние не изменяется

## Тестирование

Создан тестовый скрипт `test_drag_drop.py` для проверки API:

1. Создание тестового плана тренировок
2. Получение тренировок
3. Обновление даты тренировки
4. Проверка изменений в базе данных
5. Очистка тестовых данных

## Использование

1. Откройте страницу плана тренировок
2. Наведите курсор на тренировку - появится курсор захвата
3. Перетащите тренировку на другой день
4. Тренировка автоматически сохранится с новой датой

## Технические детали

- Используется библиотека `@dnd-kit` для React
- Collision detection: `closestCenter`
- Уникальные идентификаторы: `workout-{id}` и `day-{date}`
- Формат даты: ISO 8601 (YYYY-MM-DD)
