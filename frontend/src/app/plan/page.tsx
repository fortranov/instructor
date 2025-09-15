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
import { Workout, TrainingPlan } from '@/types/api';
import { getErrorMessage } from '@/lib/utils';

export default function PlanPage() {
  const { user, isAuthenticated, loading: authLoading } = useAuth();
  const router = useRouter();
  
  const [workouts, setWorkouts] = useState<Workout[]>([]);
  const [trainingPlan, setTrainingPlan] = useState<TrainingPlan | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [hasCheckedPlan, setHasCheckedPlan] = useState(false);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/auth/login');
    }
  }, [isAuthenticated, authLoading, router]);

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
      // Можно показать уведомление об ошибке пользователю
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
          <p className="text-gray-600 mt-2">
            Ваш персональный календарь тренировок
          </p>
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
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  <div>
                    <span className="text-sm text-gray-600">Сложность:</span>
                    <p className="font-medium">{trainingPlan.complexity}/1000</p>
                  </div>
                  <div>
                    <span className="text-sm text-gray-600">Дата соревнования:</span>
                    <p className="font-medium">
                      {new Date(trainingPlan.competition_date).toLocaleDateString('ru-RU')}
                    </p>
                  </div>
                  <div>
                    <span className="text-sm text-gray-600">Тип соревнования:</span>
                    <p className="font-medium">{trainingPlan.competition_type}</p>
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

            {/* Календарь тренировок */}
            <Calendar
              workouts={workouts}
              onMonthChange={handleMonthChange}
              onWorkoutMove={handleWorkoutMove}
              onWorkoutToggle={handleWorkoutToggle}
              loading={loading}
            />
          </>
        )}
      </div>
    </div>
  );
}
