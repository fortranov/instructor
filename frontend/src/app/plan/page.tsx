'use client';

import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '@/lib/auth-context';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import Navigation from '@/components/navigation';
import Calendar from '@/components/calendar';
import apiClient from '@/lib/api';
import { Workout, TrainingPlan, UserTariffResponse, SportType, WorkoutType } from '@/types/api';
import { getErrorMessage, getCompetitionTypeLabel } from '@/lib/utils';
import { RotateCcw } from 'lucide-react';
// import { format } from 'date-fns';
// import { ru } from 'date-fns/locale';

export default function PlanPage() {
  const { user, isAuthenticated, loading: authLoading } = useAuth();
  const router = useRouter();
  
  const [workouts, setWorkouts] = useState<Workout[]>([]);
  const [trainingPlan, setTrainingPlan] = useState<TrainingPlan | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [hasCheckedPlan, setHasCheckedPlan] = useState(false);
  const [isPortrait, setIsPortrait] = useState(false);
  const [userTariff, setUserTariff] = useState<UserTariffResponse | null>(null);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/auth/login');
    }
  }, [isAuthenticated, authLoading, router]);

  // Проверка ориентации устройства
  useEffect(() => {
    const checkOrientation = () => {
      // Проверяем, что это мобильное устройство и находится в портретной ориентации
      const isMobile = window.innerWidth <= 768;
      const isPortraitOrientation = window.innerHeight > window.innerWidth;
      setIsPortrait(isMobile && isPortraitOrientation);
    };

    // Проверяем при загрузке
    checkOrientation();

    // Добавляем слушатель изменения размера окна
    window.addEventListener('resize', checkOrientation);
    window.addEventListener('orientationchange', checkOrientation);

    // Очистка слушателей при размонтировании
    return () => {
      window.removeEventListener('resize', checkOrientation);
      window.removeEventListener('orientationchange', checkOrientation);
    };
  }, []);

  // Проверяем наличие плана у пользователя
  useEffect(() => {
    const checkUserPlan = async () => {
      if (!user?.uin || hasCheckedPlan) return;
      
      try {
        const plan = await apiClient.getTrainingPlan(user.uin);
        setTrainingPlan(plan);
      } catch (err) {
        // План не найден - это нормально для нового пользователя
        console.log('План не найден:', getErrorMessage(err));
      } finally {
        setHasCheckedPlan(true);
      }
    };

    if (user?.uin && !hasCheckedPlan) {
      checkUserPlan();
    }
  }, [user?.uin, hasCheckedPlan]);

  // Загрузка тарифа пользователя
  useEffect(() => {
    const loadUserTariff = async () => {
      if (!user) return;
      
      try {
        const tariff = await apiClient.getUserTariff();
        setUserTariff(tariff);
      } catch (err) {
        console.log('Ошибка загрузки тарифа:', getErrorMessage(err));
      }
    };

    if (user) {
      loadUserTariff();
    }
  }, [user]);

  const handleMonthChange = useCallback(async (startDate: string, endDate: string) => {
    if (!user?.uin) return;
    
    setLoading(true);
    setError('');
    
    try {
      const response = await apiClient.getWorkoutsByDateRange(user.uin, startDate, endDate);
      setWorkouts(response.workouts);
    } catch (err) {
      const errorMessage = getErrorMessage(err);
      if (!errorMessage.includes('не найден')) {
        setError(errorMessage);
      }
      setWorkouts([]);
    } finally {
      setLoading(false);
    }
  }, [user?.uin]);

  const handleDeletePlan = async () => {
    if (!user?.uin || !trainingPlan) return;
    
    if (!confirm('Вы уверены, что хотите удалить текущий план тренировок?')) {
      return;
    }
    
    try {
      await apiClient.deleteTrainingPlan(user.uin);
      setTrainingPlan(null);
      setWorkouts([]);
      alert('План тренировок успешно удален');
    } catch (err) {
      alert('Ошибка при удалении плана: ' + getErrorMessage(err));
    }
  };

  const handleWorkoutMove = async (workoutId: number, newDate: string) => {
    if (!user?.uin) return;
    
    try {
      await apiClient.updateWorkoutDate(user.uin, {
        workout_id: workoutId,
        new_date: newDate
      });
      
      // Обновить локальное состояние тренировок
      setWorkouts(prevWorkouts => 
        prevWorkouts.map(workout => 
          workout.id === workoutId 
            ? { ...workout, date: newDate }
            : workout
        )
      );
    } catch (err) {
      throw new Error(getErrorMessage(err));
    }
  };

  const handleWorkoutToggle = async (workoutId: number, date: string, isCompleted: boolean) => {
    if (!user?.uin) return;

    try {
      if (isCompleted) {
        // Отметить как выполненную
        await apiClient.markWorkoutCompleted(workoutId, {
          date: date
        });
      } else {
        // Убрать отметку о выполнении
        await apiClient.unmarkWorkoutCompleted(workoutId);
      }

      // Обновить локальное состояние тренировок
      setWorkouts(prevWorkouts =>
        prevWorkouts.map(workout =>
          workout.id === workoutId
            ? { ...workout, is_completed: isCompleted }
            : workout
        )
      );
    } catch (err) {
      console.error('Ошибка при переключении состояния тренировки:', getErrorMessage(err));
      alert('Ошибка при переключении состояния тренировки: ' + getErrorMessage(err));
    }
  };

  const handleCustomWorkoutCreate = async (date: string, sportType: SportType, durationMinutes: number, workoutType: WorkoutType) => {
    if (!user?.uin) return;

    try {
      const newWorkout = await apiClient.createCustomWorkout({
        uin: user.uin,
        date: date,
        sport_type: sportType,
        duration_minutes: durationMinutes,
        workout_type: workoutType
      });

      // Добавить новую тренировку в локальное состояние
      setWorkouts(prevWorkouts => [...prevWorkouts, newWorkout]);
    } catch (err) {
      console.error('Ошибка при создании пользовательской тренировки:', getErrorMessage(err));
      throw new Error(getErrorMessage(err));
    }
  };

  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">Загрузка...</div>
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      
      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">План тренировок</h1>
        </div>

        {error && (
          <Card className="mb-6 border-red-200">
            <CardContent className="p-4">
              <div className="text-red-600">{error}</div>
            </CardContent>
          </Card>
        )}

        {!trainingPlan ? (
          <Card className="mb-8">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <span className="text-2xl">📋</span>
                У вас пока нет плана тренировок
              </CardTitle>
              <CardDescription>
                Создайте персональный план тренировок, настроив параметры в профиле
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col sm:flex-row gap-4">
                <Link href="/profile">
                  <Button>Создать план тренировок</Button>
                </Link>
                <Link href="/dashboard">
                  <Button variant="outline">Вернуться на главную</Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        ) : (
          <>
            {/* Информация о плане */}
            <Card className="mb-6">
              <CardHeader>
                <CardTitle>Информация о плане</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  <div>
                    <span className="text-sm text-gray-600">Дата соревнования:</span>
                    <p className="font-medium">
                      {new Date(trainingPlan.competition_date).toLocaleDateString('ru-RU')}
                    </p>
                  </div>
                  <div>
                    <span className="text-sm text-gray-600">Тип соревнования:</span>
                    <p className="font-medium">{getCompetitionTypeLabel(trainingPlan.competition_type)}</p>
                  </div>
                  <div className="flex gap-2">
                    <Link href="/profile">
                      <Button variant="outline" size="sm">
                        Изменить план
                      </Button>
                    </Link>
                    <Button variant="destructive" size="sm" onClick={handleDeletePlan}>
                      Удалить план
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Календарь тренировок или сообщение о повороте устройства */}
            {isPortrait ? (
              <Card className="mb-6">
                <CardContent className="p-8 text-center">
                  <div className="flex flex-col items-center gap-4">
                    <RotateCcw className="w-16 h-16 text-blue-500 animate-pulse" />
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">
                        Поверните устройство
                      </h3>
                      <p className="text-gray-600">
                        Для удобного просмотра календаря тренировок поверните устройство в горизонтальное положение
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ) : (
              <Calendar
                workouts={workouts}
                onMonthChange={handleMonthChange}
                onWorkoutMove={handleWorkoutMove}
                onWorkoutToggle={handleWorkoutToggle}
                onCustomWorkoutCreate={handleCustomWorkoutCreate}
                loading={loading}
                userTariff={userTariff}
              />
            )}
          </>
        )}
      </div>
    </div>
  );
}
