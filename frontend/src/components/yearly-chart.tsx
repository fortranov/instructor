'use client';

import { useState, useMemo } from 'react';
import { Card } from '@/components/ui/card';

interface WeeklyStats {
  week_start: string;
  week_end: string;
  planned_duration: number;
  completed_duration: number;
  planned_workouts: number;
  completed_workouts: number;
}

interface YearlyChartProps {
  data: WeeklyStats[];
  year?: number;
}

interface WeekData {
  week_start: string;
  week_end: string;
  planned_duration: number;
  completed_duration: number;
  planned_workouts: number;
  completed_workouts: number;
}

const MONTH_NAMES = [
  'Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн',
  'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек'
];

export default function YearlyChart({ data, year }: YearlyChartProps) {
  const [isMobile, setIsMobile] = useState(false);
  
  console.log('YearlyChart props:', { data, year });

  // Определяем мобильное устройство
  useState(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    
    return () => window.removeEventListener('resize', checkMobile);
  });

  // Обрабатываем недельные данные
  const weeklyData = useMemo(() => {
    const currentYear = year || new Date().getFullYear();
    
    console.log('Processing weekly data for year:', currentYear);
    console.log('Input data:', data);
    
    // Фильтруем данные по году и сортируем по дате
    const yearWeeks = data
      .filter(week => {
        const weekStart = new Date(week.week_start);
        return weekStart.getFullYear() === currentYear;
      })
      .sort((a, b) => new Date(a.week_start).getTime() - new Date(b.week_start).getTime());
    
    console.log('Filtered weekly data:', yearWeeks);
    return yearWeeks;
  }, [data, year]);

  // Показываем все недели
  const displayData = weeklyData;

  // Группируем недели по месяцам для отображения разделителей
  const monthlyGroups = useMemo(() => {
    const groups: { [key: string]: WeeklyStats[] } = {};
    
    weeklyData.forEach(week => {
      const weekStart = new Date(week.week_start);
      const monthKey = `${weekStart.getFullYear()}-${weekStart.getMonth()}`;
      
      if (!groups[monthKey]) {
        groups[monthKey] = [];
      }
      groups[monthKey].push(week);
    });
    
    return groups;
  }, [weeklyData]);

  // Находим максимальное значение для масштабирования (максимальный недельный объем в часах)
  const maxValueHours = Math.max(
    ...weeklyData.map(week => Math.max(week.planned_duration, week.completed_duration)),
    1 // Минимальное значение для отображения
  );
  
  // Конвертируем в часы для отображения
  const maxValue = Math.ceil(maxValueHours / 60); // Округляем вверх до целых часов

  const formatDuration = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    if (hours === 0) return `${mins}м`;
    if (mins === 0) return `${hours}ч`;
    return `${hours}ч ${mins}м`;
  };

  const formatHours = (minutes: number) => {
    return Math.round(minutes / 60);
  };

  // Если нет данных, показываем сообщение
  if (!data || data.length === 0) {
    return (
      <div className="w-full text-center py-8">
        <p className="text-gray-500">Нет данных для отображения</p>
      </div>
    );
  }

  return (
    <div className="w-full">
      {/* Легенда */}
      <div className="flex justify-center gap-6 mb-6">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-blue-300 rounded"></div>
          <span className="text-sm text-gray-600">Запланировано</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-blue-600 rounded"></div>
          <span className="text-sm text-gray-600">Выполнено</span>
        </div>
      </div>

      {/* График */}
      <div className="relative">
        {/* Ось Y */}
        <div className="absolute left-0 top-0 bottom-0 w-12 flex flex-col justify-between text-xs text-gray-500">
          {[1, 0.75, 0.5, 0.25, 0].map((ratio) => (
            <div key={ratio} className="text-right pr-2">
              {Math.round(maxValue * ratio)}ч
            </div>
          ))}
        </div>

        {/* Основной график */}
        <div className="ml-12">
          <div className="flex gap-1 h-64 items-end overflow-x-auto">
            {displayData.map((week, index) => {
              const plannedHeight = maxValue > 0 ? (formatHours(week.planned_duration) / maxValue) * 100 : 0;
              const completedHeight = maxValue > 0 ? (formatHours(week.completed_duration) / maxValue) * 100 : 0;
              
              // Проверяем, нужно ли добавить разделитель месяца
              const currentWeekMonth = new Date(week.week_start).getMonth();
              const prevWeekMonth = index > 0 ? new Date(displayData[index - 1].week_start).getMonth() : null;
              const showMonthDivider = prevWeekMonth !== null && currentWeekMonth !== prevWeekMonth;
              
              // Минимальная высота в процентах для видимости (минимум 1%)
              const minHeightPercent = 1;
              const actualPlannedHeight = Math.max(plannedHeight, plannedHeight > 0 ? minHeightPercent : 0);
              const actualCompletedHeight = Math.max(completedHeight, completedHeight > 0 ? minHeightPercent : 0);
              
              // Отладочная информация
              const weekStartDate = new Date(week.week_start);
              const weekEndDate = new Date(week.week_end);
              const weekLabel = `${weekStartDate.getDate()}.${weekStartDate.getMonth() + 1}`;
              
              console.log(`Rendering week ${weekLabel}:`, {
                planned: week.planned_duration,
                completed: week.completed_duration,
                plannedHours: formatHours(week.planned_duration),
                completedHours: formatHours(week.completed_duration),
                maxValueHours: maxValueHours,
                maxValue: maxValue,
                plannedHeight: `${plannedHeight}%`,
                completedHeight: `${completedHeight}%`,
                actualPlannedHeight: `${actualPlannedHeight}%`,
                actualCompletedHeight: `${actualCompletedHeight}%`,
                calculation: {
                  plannedRatio: week.planned_duration / maxValueHours,
                  completedRatio: week.completed_duration / maxValueHours
                }
              });
              
              return (
                <div key={week.week_start} className="flex flex-col items-center flex-shrink-0 relative" style={{ width: '20px' }}>
                  {/* Вертикальный разделитель месяца */}
                  {showMonthDivider && (
                    <div className="absolute left-0 top-0 bottom-0 w-px bg-red-400 z-10"></div>
                  )}
                  
                  {/* Столбец */}
                  <div className="relative w-full h-full flex flex-col justify-end">
                    {/* Запланированная часть (светлая) */}
                    {week.planned_duration > 0 && (
                      <div
                        className="w-full bg-blue-300 rounded-t border border-blue-400"
                        style={{ 
                          height: `${actualPlannedHeight}%`
                        }}
                        title={`Запланировано: ${formatDuration(week.planned_duration)}`}
                      ></div>
                    )}
                    
                    {/* Выполненная часть (темная) */}
                    {week.completed_duration > 0 && (
                      <div
                        className="w-full bg-blue-600 rounded-b border border-blue-700"
                        style={{ 
                          height: `${actualCompletedHeight}%`
                        }}
                        title={`Выполнено: ${formatDuration(week.completed_duration)}`}
                      ></div>
                    )}
                    
                    {/* Если нет данных, показываем пустой столбец */}
                    {week.planned_duration === 0 && week.completed_duration === 0 && (
                      <div
                        className="w-full bg-gray-200 border border-gray-300"
                        style={{ height: `${minHeightPercent}%` }}
                        title="Нет данных"
                      ></div>
                    )}
                  </div>
                  
                  {/* Название недели */}
                  <div className="mt-2 text-xs text-gray-600 text-center">
                    {weekLabel}
                  </div>
                  
                  {/* Отладочная информация под столбцом */}
                  <div className="text-xs text-gray-400 text-center mt-1">
                    <div>P: {formatHours(week.planned_duration)}ч</div>
                    <div>C: {formatHours(week.completed_duration)}ч</div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
        
        {/* Разделение по месяцам */}
        <div className="ml-12 flex gap-1 mt-2">
          {Object.entries(monthlyGroups).map(([monthKey, weeks]) => {
            const monthDate = new Date(parseInt(monthKey.split('-')[0]), parseInt(monthKey.split('-')[1]));
            const monthName = MONTH_NAMES[monthDate.getMonth()];
            
            return (
              <div 
                key={monthKey} 
                className="flex-shrink-0 text-center"
                style={{ width: `${weeks.length * 21}px` }} // 20px на столбец + 1px gap
              >
                <div className="text-xs text-gray-600 font-medium">
                  {monthName}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Сетка */}
      <div className="ml-12 relative">
        {[0.25, 0.5, 0.75, 1].map((ratio, index) => (
          <div
            key={index}
            className="absolute w-full border-t border-gray-200"
            style={{ bottom: `${ratio * 100}%` }}
          ></div>
        ))}
      </div>

      {/* Альтернативное отображение данных в таблице */}
      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
        <div className="text-sm font-medium text-gray-700 mb-3">Детальные данные по неделям:</div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2 text-xs">
          {displayData.map((week) => {
            const weekStartDate = new Date(week.week_start);
            const weekLabel = `${weekStartDate.getDate()}.${weekStartDate.getMonth() + 1} - ${new Date(week.week_end).getDate()}.${new Date(week.week_end).getMonth() + 1}`;
            
            return (
              <div key={week.week_start} className="p-2 bg-white rounded border">
                <div className="font-medium text-gray-800">Неделя {weekLabel}</div>
                <div className="text-blue-600">Запланировано: {formatHours(week.planned_duration)}ч</div>
                <div className="text-green-600">Выполнено: {formatHours(week.completed_duration)}ч</div>
                <div className="text-gray-500">
                  Прогресс: {week.planned_duration > 0 ? Math.round((week.completed_duration / week.planned_duration) * 100) : 0}%
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Информация о выбранном периоде */}
      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
        <div className="text-sm text-gray-600 mb-2">
          Показаны все {displayData.length} недель
        </div>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="font-medium">Общее время (запланировано): </span>
            <span className="text-blue-600">
              {formatHours(displayData.reduce((sum, week) => sum + week.planned_duration, 0))}ч
            </span>
          </div>
          <div>
            <span className="font-medium">Общее время (выполнено): </span>
            <span className="text-green-600">
              {formatHours(displayData.reduce((sum, week) => sum + week.completed_duration, 0))}ч
            </span>
          </div>
        </div>
        
        {/* Отладочная информация */}
        <div className="mt-4 p-2 bg-yellow-50 rounded text-xs">
          <div className="font-medium text-yellow-800 mb-1">Отладочная информация:</div>
          <div>Максимальное значение: {maxValue}ч (в минутах: {maxValueHours})</div>
          <div>Количество недель: {displayData.length}</div>
          <div>Исходных недель: {data.length}</div>
          <div>Год: {year || new Date().getFullYear()}</div>
          <div className="mt-2">
            <div className="font-medium">Пример расчета:</div>
            {displayData.length > 0 && (
              <div>
                Неделя {new Date(displayData[0].week_start).getDate()}.{new Date(displayData[0].week_start).getMonth() + 1}:
                Планировано {formatHours(displayData[0].planned_duration)}ч = {Math.round((formatHours(displayData[0].planned_duration) / maxValue) * 100)}%
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
