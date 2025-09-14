'use client';

import { useState, useEffect } from 'react';
import { format, startOfMonth, endOfMonth, eachDayOfInterval, isSameMonth, isSameDay, addMonths, subMonths, startOfWeek, endOfWeek } from 'date-fns';
import { ru } from 'date-fns/locale';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Workout } from '@/types/api';
import { formatDuration, getSportIcon, getSportColor, getWorkoutTypeLabel, getWorkoutTypeColor } from '@/lib/utils';
import { ChevronLeft, ChevronRight } from 'lucide-react';

interface CalendarProps {
  workouts: Workout[];
  onMonthChange: (startDate: string, endDate: string) => void;
  loading?: boolean;
}

export default function Calendar({ workouts, onMonthChange, loading = false }: CalendarProps) {
  const [currentDate, setCurrentDate] = useState(new Date());
  
  useEffect(() => {
    const start = format(startOfMonth(currentDate), 'yyyy-MM-dd');
    const end = format(endOfMonth(currentDate), 'yyyy-MM-dd');
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

  const getWorkoutsForDay = (day: Date) => {
    return workouts.filter(workout => 
      isSameDay(new Date(workout.date), day)
    );
  };

  const navigateMonth = (direction: 'prev' | 'next') => {
    setCurrentDate(prev => 
      direction === 'prev' ? subMonths(prev, 1) : addMonths(prev, 1)
    );
  };

  const weekDays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];

  return (
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
            <div className="grid grid-cols-7 gap-1">
              {/* Заголовки дней недели */}
              {weekDays.map(day => (
                <div key={day} className="p-2 text-center text-sm font-medium text-gray-500">
                  {day}
                </div>
              ))}

              {/* Дни месяца */}
              {calendarDays.map((day, index) => {
                const dayWorkouts = getWorkoutsForDay(day);
                const isCurrentMonth = isSameMonth(day, currentDate);
                const isToday = isSameDay(day, new Date());

                return (
                  <div
                    key={index}
                    className={`
                      min-h-[100px] p-1 border border-gray-200 bg-white
                      ${!isCurrentMonth ? 'bg-gray-50 text-gray-400' : ''}
                      ${isToday ? 'bg-blue-50 border-blue-200' : ''}
                    `}
                  >
                    <div className={`
                      text-sm font-medium mb-1
                      ${isToday ? 'text-blue-600' : ''}
                    `}>
                      {format(day, 'd')}
                    </div>
                    
                    <div className="space-y-1">
                      {dayWorkouts.map((workout, workoutIndex) => (
                        <div
                          key={workoutIndex}
                          className="text-xs p-1 rounded bg-white border shadow-sm hover:shadow-md transition-shadow cursor-pointer"
                          title={`${getSportIcon(workout.sport_type)} ${getWorkoutTypeLabel(workout.workout_type)} - ${formatDuration(workout.duration_minutes)}`}
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
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Легенда */}
      <Card>
        <CardContent className="p-4">
          <h3 className="text-sm font-medium mb-3">Обозначения</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h4 className="text-xs font-medium text-gray-600 mb-2">Виды спорта:</h4>
              <div className="space-y-1 text-xs">
                <div className="flex items-center gap-2">
                  <span className="text-base">🏃</span>
                  <span className="w-3 h-3 bg-red-500 rounded-full"></span>
                  <span>Бег</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-base">🚴</span>
                  <span className="w-3 h-3 bg-blue-500 rounded-full"></span>
                  <span>Велосипед</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-base">🏊</span>
                  <span className="w-3 h-3 bg-cyan-500 rounded-full"></span>
                  <span>Плавание</span>
                </div>
              </div>
            </div>
            
            <div>
              <h4 className="text-xs font-medium text-gray-600 mb-2">Типы тренировок:</h4>
              <div className="space-y-1 text-xs">
                <div className="flex items-center gap-2">
                  <span className="px-2 py-1 bg-green-100 text-green-800 rounded">Длительная</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="px-2 py-1 bg-orange-100 text-orange-800 rounded">Интервальная</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded">Восстанавливающая</span>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
