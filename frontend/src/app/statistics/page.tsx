'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth-context';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import YearlyChart from '@/components/yearly-chart';
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
      setYearlyStats(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка загрузки данных');
    } finally {
      setLoading(false);
    }
  };

  const formatDuration = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours}ч ${mins}м`;
  };

  const getCompletionRate = (completed: number, planned: number) => {
    if (planned === 0) return 0;
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
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Статистика тренировок
          </h1>
          <p className="text-gray-600">
            Анализ выполнения плана тренировок по неделям и месяцам
          </p>
        </div>

        {/* Селектор года */}
        <Card className="p-6 mb-8">
          <div className="flex flex-wrap items-center gap-4">
            <label className="text-sm font-medium text-gray-700">
              Выберите год:
            </label>
            <div className="flex gap-2">
              {availableYears.map((year) => (
                <Button
                  key={year}
                  variant={selectedYear === year ? "default" : "outline"}
                  size="sm"
                  onClick={() => setSelectedYear(year)}
                >
                  {year}
                </Button>
              ))}
            </div>
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
            {/* Общая статистика */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <Card className="p-6">
                <h3 className="text-sm font-medium text-gray-500 mb-2">
                  Общее время (запланировано)
                </h3>
                <p className="text-2xl font-bold text-blue-600">
                  {formatDuration(yearlyStats.total_planned_duration)}
                </p>
              </Card>
              
              <Card className="p-6">
                <h3 className="text-sm font-medium text-gray-500 mb-2">
                  Общее время (выполнено)
                </h3>
                <p className="text-2xl font-bold text-green-600">
                  {formatDuration(yearlyStats.total_completed_duration)}
                </p>
              </Card>
              
              <Card className="p-6">
                <h3 className="text-sm font-medium text-gray-500 mb-2">
                  Тренировки (запланировано)
                </h3>
                <p className="text-2xl font-bold text-blue-600">
                  {yearlyStats.total_planned_workouts}
                </p>
              </Card>
              
              <Card className="p-6">
                <h3 className="text-sm font-medium text-gray-500 mb-2">
                  Тренировки (выполнено)
                </h3>
                <p className="text-2xl font-bold text-green-600">
                  {yearlyStats.total_completed_workouts}
                </p>
              </Card>
            </div>

            {/* Процент выполнения */}
            <Card className="p-6 mb-8">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Процент выполнения за {selectedYear} год
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm font-medium text-gray-700">
                      По времени
                    </span>
                    <span className="text-sm font-medium text-gray-900">
                      {getCompletionRate(
                        yearlyStats.total_completed_duration,
                        yearlyStats.total_planned_duration
                      )}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{
                        width: `${getCompletionRate(
                          yearlyStats.total_completed_duration,
                          yearlyStats.total_planned_duration
                        )}%`,
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
                      {getCompletionRate(
                        yearlyStats.total_completed_workouts,
                        yearlyStats.total_planned_workouts
                      )}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-green-600 h-2 rounded-full"
                      style={{
                        width: `${getCompletionRate(
                          yearlyStats.total_completed_workouts,
                          yearlyStats.total_planned_workouts
                        )}%`,
                      }}
                    ></div>
                  </div>
                </div>
              </div>
            </Card>

            {/* Годовой график */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                График тренировок за {selectedYear} год
              </h3>
              <YearlyChart data={yearlyStats.weekly_stats} />
            </Card>
          </>
        )}
      </div>
    </div>
  );
}
