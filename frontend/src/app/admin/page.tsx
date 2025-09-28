'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Users, CreditCard, Settings } from 'lucide-react';

interface AdminStats {
  totalUsers: number;
  activeUsers: number;
  totalPlans: number;
}

export default function AdminDashboard() {
  const [stats, setStats] = useState<AdminStats>({
    totalUsers: 0,
    activeUsers: 0,
    totalPlans: 0
  });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        // Здесь можно добавить API для получения статистики
        // Пока используем заглушку
        setStats({
          totalUsers: 0,
          activeUsers: 0,
          totalPlans: 0
        });
      } catch (error) {
        console.error('Ошибка загрузки статистики:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchStats();
  }, []);

  const dashboardCards = [
    {
      title: 'Пользователи',
      description: 'Управление пользователями и их тарифами',
      icon: Users,
      href: '/admin/users',
      color: 'bg-blue-500',
      stat: `${stats.totalUsers} пользователей`
    },
    {
      title: 'Тарифы',
      description: 'Настройка функционала тарифных планов',
      icon: CreditCard,
      href: '/admin/tariffs',
      color: 'bg-green-500',
      stat: '3 тарифа'
    },
    {
      title: 'Настройки тренировок',
      description: 'Редактирование коэффициентов планов',
      icon: Settings,
      href: '/admin/workout-settings',
      color: 'bg-purple-500',
      stat: 'Коэффициенты'
    }
  ];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Панель администратора</h1>
        <p className="mt-2 text-gray-600">
          Добро пожаловать в панель администрирования Triplan
        </p>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {dashboardCards.map((card) => (
          <Link
            key={card.href}
            href={card.href}
            className="block p-6 bg-white rounded-lg shadow hover:shadow-md transition-shadow"
          >
            <div className="flex items-center">
              <div className={`p-3 rounded-lg ${card.color}`}>
                <card.icon className="h-6 w-6 text-white" />
              </div>
              <div className="ml-4 flex-1">
                <h3 className="text-lg font-semibold text-gray-900">
                  {card.title}
                </h3>
                <p className="text-sm text-gray-600 mt-1">
                  {card.description}
                </p>
                <p className="text-sm font-medium text-gray-900 mt-2">
                  {card.stat}
                </p>
              </div>
            </div>
          </Link>
        ))}
      </div>

      {/* Quick actions */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Быстрые действия
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Link
            href="/admin/users"
            className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <Users className="h-5 w-5 text-blue-500 mr-3" />
            <div>
              <div className="font-medium text-gray-900">Просмотреть пользователей</div>
              <div className="text-sm text-gray-600">Управление пользователями и тарифами</div>
            </div>
          </Link>
          
          <Link
            href="/admin/tariffs"
            className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <CreditCard className="h-5 w-5 text-green-500 mr-3" />
            <div>
              <div className="font-medium text-gray-900">Настроить тарифы</div>
              <div className="text-sm text-gray-600">Изменить функционал тарифов</div>
            </div>
          </Link>
        </div>
      </div>
    </div>
  );
}
