'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth-context';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import YearlyChart from '@/components/yearly-chart';
import Navigation from '@/components/navigation';
import apiClient from '@/lib/api';

interface WeeklyStats {
  week_start: string;
  week_end: string;
  planned_duration: number;
  completed_duration: number;
  planned_workouts: number;
  completed_workouts: number;
}

interface YearlyStats {
  year: number;
  total_planned_duration: number;
  total_completed_duration: number;
  total_planned_workouts: number;
  total_completed_workouts: number;
  weekly_stats: WeeklyStats[];
}

export default function StatisticsPage() {
  const { user } = useAuth();
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [availableYears, setAvailableYears] = useState<number[]>([]);
  const [yearlyStats, setYearlyStats] = useState<YearlyStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const handleYearChange = (newYear: number) => {
    if (availableYears.includes(newYear)) {
      setSelectedYear(newYear);
    }
  };

  useEffect(() => {
    fetchAvailableYears();
  }, []);

  useEffect(() => {
    if (selectedYear) {
      fetchYearlyStats(selectedYear);
    }
  }, [selectedYear]);

  const fetchAvailableYears = async () => {
    try {
      const data = await apiClient.getAvailableYears();
      setAvailableYears(data.years);
      
      // Установить текущий год, если он доступен, иначе первый доступный год
      if (data.years.includes(new Date().getFullYear())) {
        setSelectedYear(new Date().getFullYear());
      } else if (data.years.length > 0) {
        setSelectedYear(data.years[data.years.length - 1]);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка загрузки данных');
    }
  };

  const fetchYearlyStats = async (year: number) => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await apiClient.getYearlyStatistics(year);
      console.log('Statistics data received:', data);
      setYearlyStats(data);
    } catch (err) {
      console.error('Error fetching statistics:', err);
      setError(err instanceof Error ? err.message : 'Ошибка загрузки данных');
    } finally {
      setLoading(false);
    }
  };


  const getCompletionRateUpToToday = (completed: number, planned: number) => {
    if (planned === 0) return 0;
    
    // Рассчитываем процент выполнения только до сегодняшнего дня
    const today = new Date();
    const yearStart = new Date(selectedYear, 0, 1);
    const yearEnd = new Date(selectedYear, 11, 31);
    
    // Если текущий год, считаем только до сегодня
    if (selectedYear === today.getFullYear()) {
      const totalDays = Math.floor((today.getTime() - yearStart.getTime()) / (1000 * 60 * 60 * 24));
      const totalYearDays = Math.floor((yearEnd.getTime() - yearStart.getTime()) / (1000 * 60 * 60 * 24));
      const plannedUpToToday = (planned * totalDays) / totalYearDays;
      
      return Math.round((completed / plannedUpToToday) * 100);
    }
    
    // Для прошлых лет считаем весь год
    return Math.round((completed / planned) * 100);
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Card className="p-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Доступ запрещен
          </h2>
          <p className="text-gray-600">
            Для просмотра статистики необходимо войти в систему.
          </p>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      
      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Статистика тренировок
          </h1>
          <p className="text-gray-600">
            Анализ выполнения плана тренировок по неделям и месяцам
          </p>
        </div>

        {/* Селектор года со стрелками */}
        <Card className="p-6 mb-8">
          <div className="flex items-center justify-center gap-4">
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleYearChange(selectedYear - 1)}
              disabled={!availableYears.includes(selectedYear - 1)}
            >
              ←
            </Button>
            <div className="text-xl font-semibold text-gray-900">
              {selectedYear}
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleYearChange(selectedYear + 1)}
              disabled={!availableYears.includes(selectedYear + 1)}
            >
              →
            </Button>
          </div>
        </Card>

        {loading && (
          <Card className="p-8 text-center">
            <div className="text-gray-600">Загрузка статистики...</div>
          </Card>
        )}

        {error && (
          <Card className="p-8 text-center">
            <div className="text-red-600 mb-4">{error}</div>
            <Button onClick={() => fetchYearlyStats(selectedYear)}>
              Попробовать снова
            </Button>
          </Card>
        )}

        {yearlyStats && !loading && !error && (
          <>
            {/* Процент выполнения */}
            <Card className="p-6 mb-8">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Процент выполнения за {selectedYear} год
                {selectedYear === new Date().getFullYear() && (
                  <span className="text-sm font-normal text-gray-500 ml-2">
                    (до сегодняшнего дня)
                  </span>
                )}
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm font-medium text-gray-700">
                      По времени
                    </span>
                    <span className="text-sm font-medium text-gray-900">
                      {getCompletionRateUpToToday(
                        yearlyStats.total_completed_duration,
                        yearlyStats.total_planned_duration
                      )}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{
                        width: `${Math.min(100, getCompletionRateUpToToday(
                          yearlyStats.total_completed_duration,
                          yearlyStats.total_planned_duration
                        ))}%`,
                      }}
                    ></div>
                  </div>
                </div>
                
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm font-medium text-gray-700">
                      По количеству тренировок
                    </span>
                    <span className="text-sm font-medium text-gray-900">
                      {getCompletionRateUpToToday(
                        yearlyStats.total_completed_workouts,
                        yearlyStats.total_planned_workouts
                      )}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-green-600 h-2 rounded-full"
                      style={{
                        width: `${Math.min(100, getCompletionRateUpToToday(
                          yearlyStats.total_completed_workouts,
                          yearlyStats.total_planned_workouts
                        ))}%`,
                      }}
                    ></div>
                  </div>
                </div>
              </div>
            </Card>

            {/* Недельный график */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Недельные объемы тренировок за {selectedYear} год
              </h3>
              <YearlyChart data={yearlyStats.weekly_stats} year={selectedYear} />
            </Card>
          </>
        )}
      </div>
    </div>
  );
}
