'use client';

import { useAuth } from '@/lib/auth-context';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import Navigation from '@/components/navigation';

export default function DashboardPage() {
  const { user, isAuthenticated, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.push('/auth/login');
    }
  }, [isAuthenticated, loading, router]);

  if (loading) {
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
          <h1 className="text-3xl font-bold text-gray-900">
            Добро пожаловать{user.first_name ? `, ${user.first_name}` : ''}!
          </h1>
          <p className="text-gray-600 mt-2">
            Управляйте своими планами тренировок и достигайте спортивных целей
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <span className="text-2xl">📅</span>
                План тренировок
              </CardTitle>
              <CardDescription>
                Просматривайте и управляйте вашим планом тренировок
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Link href="/plan">
                <Button className="w-full">Открыть план</Button>
              </Link>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <span className="text-2xl">⚙️</span>
                Профиль
              </CardTitle>
              <CardDescription>
                Настройте сложность плана и параметры соревнований
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Link href="/profile">
                <Button variant="outline" className="w-full">Настроить профиль</Button>
              </Link>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <span className="text-2xl">📊</span>
                Статистика
              </CardTitle>
              <CardDescription>
                Отслеживайте прогресс и анализируйте результаты
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Link href="/statistics">
                <Button variant="outline" className="w-full">
                  Открыть статистику
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Быстрый старт</CardTitle>
              <CardDescription>
                Начните создавать свой первый план тренировок
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-start gap-3">
                <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-blue-600 text-sm font-semibold">1</span>
                </div>
                <div>
                  <h4 className="font-medium">Настройте профиль</h4>
                  <p className="text-sm text-gray-600">
                    Укажите уровень сложности и цели соревнований
                  </p>
                </div>
              </div>
              
              <div className="flex items-start gap-3">
                <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-blue-600 text-sm font-semibold">2</span>
                </div>
                <div>
                  <h4 className="font-medium">Создайте план</h4>
                  <p className="text-sm text-gray-600">
                    Система автоматически создаст персональный план тренировок
                  </p>
                </div>
              </div>
              
              <div className="flex items-start gap-3">
                <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-blue-600 text-sm font-semibold">3</span>
                </div>
                <div>
                  <h4 className="font-medium">Следуйте плану</h4>
                  <p className="text-sm text-gray-600">
                    Выполняйте тренировки согласно календарю и достигайте целей
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Информация о пользователе</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <span className="text-sm text-gray-600">Email:</span>
                <p className="font-medium">{user.email}</p>
              </div>
              
              {user.first_name && (
                <div>
                  <span className="text-sm text-gray-600">Имя:</span>
                  <p className="font-medium">{user.first_name}</p>
                </div>
              )}
              
              {user.last_name && (
                <div>
                  <span className="text-sm text-gray-600">Фамилия:</span>
                  <p className="font-medium">{user.last_name}</p>
                </div>
              )}
              
              <div>
                <span className="text-sm text-gray-600">Дата регистрации:</span>
                <p className="font-medium">
                  {new Date(user.created_at).toLocaleDateString('ru-RU')}
                </p>
              </div>
              
              <div className="pt-4">
                <Link href="/profile">
                  <Button variant="outline" size="sm">
                    Редактировать профиль
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
