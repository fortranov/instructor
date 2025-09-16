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

interface MonthData {
  name: string;
  weeks: WeeklyStats[];
  totalPlanned: number;
  totalCompleted: number;
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

  // Группируем данные по месяцам
  const monthlyData = useMemo(() => {
    const months: MonthData[] = [];
    const currentYear = year || new Date().getFullYear();
    
    // Создаем 12 месяцев
    for (let i = 0; i < 12; i++) {
      const monthStart = new Date(currentYear, i, 1);
      const monthEnd = new Date(currentYear, i + 1, 0);
      
      const monthWeeks = data.filter(week => {
        const weekStart = new Date(week.week_start);
        const weekEnd = new Date(week.week_end);
        
        // Проверяем пересечение недели с месяцем
        return (weekStart <= monthEnd && weekEnd >= monthStart);
      });
      
      const totalPlanned = monthWeeks.reduce((sum, week) => sum + week.planned_duration, 0);
      const totalCompleted = monthWeeks.reduce((sum, week) => sum + week.completed_duration, 0);
      
      months.push({
        name: MONTH_NAMES[i],
        weeks: monthWeeks,
        totalPlanned,
        totalCompleted
      });
    }
    
    console.log('Monthly data calculated:', months);
    return months;
  }, [data, year]);

  // Для мобильных устройств показываем только 2 месяца
  const displayData = isMobile ? monthlyData.slice(0, 2) : monthlyData;

  // Находим максимальное значение для масштабирования
  const maxValue = Math.max(
    ...monthlyData.map(month => Math.max(month.totalPlanned, month.totalCompleted))
  );

  const formatDuration = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    if (hours === 0) return `${mins}м`;
    if (mins === 0) return `${hours}ч`;
    return `${hours}ч ${mins}м`;
  };

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
              {formatDuration(Math.round(maxValue * ratio))}
            </div>
          ))}
        </div>

        {/* Основной график */}
        <div className="ml-12">
          <div className="grid grid-cols-12 gap-1 h-64 items-end">
            {displayData.map((month, index) => {
              const plannedHeight = maxValue > 0 ? (month.totalPlanned / maxValue) * 100 : 0;
              const completedHeight = maxValue > 0 ? (month.totalCompleted / maxValue) * 100 : 0;
              
              return (
                <div key={month.name} className="flex flex-col items-center">
                  {/* Столбец */}
                  <div className="relative w-full max-w-8 h-full flex flex-col justify-end">
                    {/* Запланированная часть (светлая) */}
                    <div
                      className="w-full bg-blue-300 rounded-t"
                      style={{ height: `${plannedHeight}%` }}
                      title={`Запланировано: ${formatDuration(month.totalPlanned)}`}
                    ></div>
                    
                    {/* Выполненная часть (темная) */}
                    <div
                      className="w-full bg-blue-600 rounded-b"
                      style={{ height: `${completedHeight}%` }}
                      title={`Выполнено: ${formatDuration(month.totalCompleted)}`}
                    ></div>
                  </div>
                  
                  {/* Название месяца */}
                  <div className="mt-2 text-xs text-gray-600 text-center">
                    {month.name}
                  </div>
                </div>
              );
            })}
          </div>
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

      {/* Информация о выбранном периоде */}
      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
        <div className="text-sm text-gray-600 mb-2">
          {isMobile ? 'Показаны первые 2 месяца' : 'Показаны все 12 месяцев'}
        </div>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="font-medium">Общее время (запланировано): </span>
            <span className="text-blue-600">
              {formatDuration(displayData.reduce((sum, month) => sum + month.totalPlanned, 0))}
            </span>
          </div>
          <div>
            <span className="font-medium">Общее время (выполнено): </span>
            <span className="text-green-600">
              {formatDuration(displayData.reduce((sum, month) => sum + month.totalCompleted, 0))}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
