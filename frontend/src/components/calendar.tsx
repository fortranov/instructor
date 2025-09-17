'use client';

import { useState, useEffect } from 'react';
import { format, startOfMonth, endOfMonth, eachDayOfInterval, isSameMonth, isSameDay, addMonths, subMonths, startOfWeek, endOfWeek, isSameWeek } from 'date-fns';
import { ru } from 'date-fns/locale';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Workout, SportType } from '@/types/api';
import { formatDuration, getSportIcon, getSportColor, getSportLabel, getWorkoutTypeLabel, getWorkoutTypeColor } from '@/lib/utils';
import { ChevronLeft, ChevronRight, Move } from 'lucide-react';
import WorkoutModal from './workout-modal';
import {
  DndContext,
  DragEndEvent,
  DragOverlay,
  DragStartEvent,
  useDraggable,
  useDroppable,
  closestCenter,
} from '@dnd-kit/core';
import { CSS } from '@dnd-kit/utilities';

interface CalendarProps {
  workouts: Workout[];
  onMonthChange: (startDate: string, endDate: string) => void;
  onWorkoutMove?: (workoutId: number, newDate: string) => Promise<void>;
  onWorkoutToggle?: (workoutId: number, date: string, isCompleted: boolean) => Promise<void>;
  loading?: boolean;
}

// Компонент перетаскиваемой тренировки
// eslint-disable-next-line @typescript-eslint/no-unsafe-function-type, @typescript-eslint/no-explicit-any
function DraggableWorkout({ workout, children }: { workout: Workout; children: (props: { listeners: Record<string, Function> | undefined; attributes: Record<string, any> }) => React.ReactNode }) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    isDragging,
  } = useDraggable({
    id: `workout-${workout.id}`,
    data: {
      workout,
    },
  });

  const style = {
    transform: CSS.Translate.toString(transform),
    opacity: isDragging ? 0.5 : 1,
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
    >
      {children({ listeners, attributes })}
    </div>
  );
}

// Компонент дропзоны для дня
function DroppableDay({ 
  day, 
  children, 
  isDropAllowed = true 
}: { 
  day: Date; 
  children: React.ReactNode;
  isDropAllowed?: boolean;
}) {
  const { isOver, setNodeRef } = useDroppable({
    id: `day-${format(day, 'yyyy-MM-dd')}`,
    data: {
      date: format(day, 'yyyy-MM-dd'),
    },
    disabled: !isDropAllowed,
  });

  return (
    <div
      ref={setNodeRef}
      className={`
        min-h-[100px] p-1 border border-gray-200 transition-colors
        ${isDropAllowed 
          ? 'bg-white' 
          : 'bg-gray-50 opacity-50'
        }
        ${isOver && isDropAllowed ? 'bg-blue-50 border-blue-300' : ''}
        ${!isDropAllowed ? 'cursor-not-allowed' : ''}
      `}
    >
      {children}
    </div>
  );
}

export default function Calendar({ workouts, onMonthChange, onWorkoutMove, onWorkoutToggle, loading = false }: CalendarProps) {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [activeWorkout, setActiveWorkout] = useState<Workout | null>(null);
  const [draggedWorkoutWeek, setDraggedWorkoutWeek] = useState<Date | null>(null);
  const [selectedWorkout, setSelectedWorkout] = useState<Workout | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  
  useEffect(() => {
    // Загружаем тренировки для всего диапазона календаря, включая дни предыдущего и следующего месяца
    const monthStart = startOfMonth(currentDate);
    const monthEnd = endOfMonth(currentDate);
    const calendarStart = startOfWeek(monthStart, { weekStartsOn: 1 });
    const calendarEnd = endOfWeek(monthEnd, { weekStartsOn: 1 });
    
    const start = format(calendarStart, 'yyyy-MM-dd');
    const end = format(calendarEnd, 'yyyy-MM-dd');
    onMonthChange(start, end);
  }, [currentDate, onMonthChange]);

  const monthStart = startOfMonth(currentDate);
  const monthEnd = endOfMonth(currentDate);
  const calendarStart = startOfWeek(monthStart, { weekStartsOn: 1 });
  const calendarEnd = endOfWeek(monthEnd, { weekStartsOn: 1 });
  
  const calendarDays = eachDayOfInterval({
    start: calendarStart,
    end: calendarEnd,
  });

  // Группируем дни по неделям
  const weekRows = [];
  for (let i = 0; i < calendarDays.length; i += 7) {
    weekRows.push(calendarDays.slice(i, i + 7));
  }

  const getWorkoutsForDay = (day: Date) => {
    return workouts.filter(workout => 
      isSameDay(new Date(workout.date), day)
    );
  };

  // Функция для получения тренировок недели
  const getWorkoutsForWeek = (day: Date) => {
    return workouts.filter(workout => 
      isSameWeek(new Date(workout.date), day, { weekStartsOn: 1 })
    );
  };

  // Функция для группировки тренировок по видам спорта с суммированием времени
  const getWeeklySportSummary = (day: Date) => {
    const weekWorkouts = getWorkoutsForWeek(day);
    const summary = new Map<string, number>();
    
    weekWorkouts.forEach(workout => {
      const sportType = workout.sport_type;
      const currentTime = summary.get(sportType) || 0;
      summary.set(sportType, currentTime + workout.duration_minutes);
    });
    
    return Array.from(summary.entries()).map(([sportType, totalMinutes]) => ({
      sportType: sportType as SportType,
      totalMinutes
    }));
  };

  const navigateMonth = (direction: 'prev' | 'next') => {
    setCurrentDate(prev => 
      direction === 'prev' ? subMonths(prev, 1) : addMonths(prev, 1)
    );
  };

  const handleWorkoutToggle = async (workoutId: number, date: string, currentStatus: boolean) => {
    if (!onWorkoutToggle) return;
    
    try {
      await onWorkoutToggle(workoutId, date, !currentStatus);
    } catch (error) {
      console.error('Ошибка при переключении состояния тренировки:', error);
    }
  };

  const handleWorkoutClick = (workout: Workout) => {
    setSelectedWorkout(workout);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedWorkout(null);
  };

  const handleDragStart = (event: DragStartEvent) => {
    const { active } = event;
    const workout = active.data.current?.workout;
    if (workout) {
      setActiveWorkout(workout);
      // Запоминаем неделю, к которой принадлежит перетаскиваемая тренировка
      setDraggedWorkoutWeek(new Date(workout.date));
    }
  };

  const handleDragEnd = async (event: DragEndEvent) => {
    const { active, over } = event;
    
    setActiveWorkout(null);
    setDraggedWorkoutWeek(null);
    
    if (!over || !onWorkoutMove) return;
    
    const workout = active.data.current?.workout;
    const newDate = over.data.current?.date;
    
    if (workout && newDate && workout.date !== newDate) {
      // Проверяем, что тренировка перемещается в пределах той же недели
      const originalWeek = new Date(workout.date);
      const targetWeek = new Date(newDate);
      
      if (!isSameWeek(originalWeek, targetWeek, { weekStartsOn: 1 })) {
        console.warn('Тренировку можно перемещать только в пределах одной недели');
        return;
      }
      
      try {
        await onWorkoutMove(workout.id, newDate);
      } catch (error) {
        console.error('Ошибка при перемещении тренировки:', error);
        // Здесь можно добавить уведомление об ошибке
      }
    }
  };

  const weekDays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];

  return (
    <DndContext
      collisionDetection={closestCenter}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
    >
      <div className="space-y-4">
        {/* Заголовок календаря */}
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold">
            {format(currentDate, 'LLLL yyyy', { locale: ru })}
          </h2>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => navigateMonth('prev')}
              disabled={loading}
            >
              <ChevronLeft className="w-4 h-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => navigateMonth('next')}
              disabled={loading}
            >
              <ChevronRight className="w-4 h-4" />
            </Button>
          </div>
        </div>

      {/* Календарная сетка */}
      <Card>
        <CardContent className="p-4">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="text-gray-500">Загрузка тренировок...</div>
            </div>
          ) : (
            <div className="grid grid-cols-8 gap-1">
              {/* Заголовки дней недели */}
              {weekDays.map(day => (
                <div key={day} className="p-2 text-center text-sm font-medium text-gray-500">
                  {day}
                </div>
              ))}
              {/* Заголовок колонки суммы */}
              <div className="p-2 text-center text-sm font-medium text-gray-500">
                Итого за неделю
              </div>

              {/* Строки недель */}
              {weekRows.map((weekDays, weekIndex) => (
                <>
                  {/* Дни недели */}
                  {weekDays.map((day, dayIndex) => {
                    const dayWorkouts = getWorkoutsForDay(day);
                    const isCurrentMonth = isSameMonth(day, currentDate);
                    const isToday = isSameDay(day, new Date());
                    
                    // Определяем, разрешен ли дроп в этот день
                    const isDropAllowed = !draggedWorkoutWeek || isSameWeek(day, draggedWorkoutWeek, { weekStartsOn: 1 });

                    return (
                      <DroppableDay key={`${weekIndex}-${dayIndex}`} day={day} isDropAllowed={isDropAllowed}>
                        <div className={`
                          relative
                          ${!isCurrentMonth ? 'bg-gray-50 text-gray-400' : ''}
                          ${isToday ? 'bg-blue-50 border-blue-200' : ''}
                        `}>
                          <div className="mb-1">
                            <div className={`
                              text-sm font-medium
                              ${isToday ? 'text-blue-600' : ''}
                            `}>
                              {format(day, 'd')}
                            </div>
                          </div>
                          
                          <div className="space-y-1">
                            {dayWorkouts.map((workout, workoutIndex) => (
                              <DraggableWorkout key={workoutIndex} workout={workout}>
                                {({ listeners, attributes }) => (
                                  <div
                                    className={`
                                      text-xs p-1 rounded border shadow-sm hover:shadow-md transition-shadow relative
                                      ${workout.is_completed 
                                        ? 'bg-green-50 border-green-200' 
                                        : 'bg-white border-gray-200'
                                      }
                                    `}
                                    title={`${getSportIcon(workout.sport_type)} ${getWorkoutTypeLabel(workout.workout_type)} - ${formatDuration(workout.duration_minutes)}`}
                                  >
                                    {/* Кнопка drag-and-drop в правом верхнем углу */}
                                    <button
                                      className="absolute top-1 right-1 w-5 h-5 rounded-sm border-2 bg-blue-500 border-blue-500 text-white hover:bg-blue-600 flex items-center justify-center text-xs transition-all z-50 cursor-grab active:cursor-grabbing"
                                      title="Перетащить тренировку"
                                      style={{ pointerEvents: 'auto' }}
                                      {...listeners}
                                      {...attributes}
                                    >
                                      <Move className="w-3 h-3" />
                                    </button>

                                    {/* Галочка выполнения в правом верхнем углу (смещена влево) */}
                                    <button
                                      onClick={(e) => {
                                        e.stopPropagation();
                                        e.preventDefault();
                                        handleWorkoutToggle(workout.id, workout.date, workout.is_completed || false);
                                      }}
                                      className={`
                                        absolute top-1 right-7 w-5 h-5 rounded-sm border-2 flex items-center justify-center text-xs transition-all z-50 cursor-pointer
                                        ${workout.is_completed 
                                          ? 'bg-green-500 border-green-500 text-white hover:bg-green-600' 
                                          : 'bg-gray-300 border-gray-300 text-gray-500 hover:bg-gray-400'
                                        }
                                      `}
                                      title={workout.is_completed ? 'Тренировка выполнена' : 'Отметить как выполненную'}
                                      style={{ pointerEvents: 'auto' }}
                                    >
                                      {workout.is_completed && '✓'}
                                    </button>

                                    {/* Основная область карточки - клик для открытия модального окна */}
                                    <div 
                                      className="cursor-pointer pr-12"
                                      onClick={() => handleWorkoutClick(workout)}
                                    >
                                      <div className="flex items-center gap-1 mb-1">
                                        <span className="text-sm">{getSportIcon(workout.sport_type)}</span>
                                        <span className={`
                                          inline-block w-2 h-2 rounded-full flex-shrink-0
                                          ${getSportColor(workout.sport_type)}
                                        `}></span>
                                      </div>
                                      
                                      <div className="text-xs text-gray-600 truncate">
                                        {formatDuration(workout.duration_minutes)}
                                      </div>
                                      
                                      <div className={`
                                        text-xs px-1 py-0.5 rounded text-center truncate
                                        ${getWorkoutTypeColor(workout.workout_type)}
                                      `}>
                                        {getWorkoutTypeLabel(workout.workout_type)}
                                      </div>
                                    </div>
                                  </div>
                                )}
                              </DraggableWorkout>
                            ))}
                          </div>
                        </div>
                      </DroppableDay>
                    );
                  })}
                  
                  {/* Колонка с суммарным временем за неделю */}
                  <div key={`summary-${weekIndex}`} className="min-h-[100px] p-2 border border-gray-200 bg-gray-50">
                    <div className="space-y-2">
                      {getWeeklySportSummary(weekDays[0]).map(({ sportType, totalMinutes }) => (
                        <div key={sportType} className="text-xs">
                          <div className="flex items-center gap-1 mb-1">
                            <span className="text-sm">{getSportIcon(sportType)}</span>
                            <span className={`
                              inline-block w-2 h-2 rounded-full flex-shrink-0
                              ${getSportColor(sportType)}
                            `}></span>
                          </div>
                          <div className="text-xs text-gray-600 mb-1">
                            {getSportLabel(sportType)}
                          </div>
                          <div className="font-medium text-gray-700">
                            {formatDuration(totalMinutes)}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
      </div>

      {/* DragOverlay для отображения перетаскиваемого элемента */}
      <DragOverlay>
        {activeWorkout ? (
          <div className="text-xs p-1 rounded bg-white border shadow-lg opacity-90">
            <div className="flex items-center gap-1 mb-1">
              <span className="text-sm">{getSportIcon(activeWorkout.sport_type)}</span>
              <span className={`
                inline-block w-2 h-2 rounded-full flex-shrink-0
                ${getSportColor(activeWorkout.sport_type)}
              `}></span>
            </div>
            
            <div className="text-xs text-gray-600 truncate">
              {formatDuration(activeWorkout.duration_minutes)}
            </div>
            
            <div className={`
              text-xs px-1 py-0.5 rounded text-center truncate
              ${getWorkoutTypeColor(activeWorkout.workout_type)}
            `}>
              {getWorkoutTypeLabel(activeWorkout.workout_type)}
            </div>
          </div>
        ) : null}
      </DragOverlay>

      {/* Модальное окно с описанием тренировки */}
      <WorkoutModal
        workout={selectedWorkout}
        isOpen={isModalOpen}
        onClose={handleCloseModal}
      />
    </DndContext>
  );
}
