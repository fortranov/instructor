'use client';

import { useEffect, useState } from 'react';
import { MoreVertical, Search, Filter } from 'lucide-react';

interface User {
  id: number;
  uin: string;
  email: string;
  first_name: string | null;
  last_name: string | null;
  is_active: boolean;
  tariff_type: string | null;
  tariff_name: string | null;
  created_at: string;
}

interface TariffMenuProps {
  user: User;
  onTariffChange: (userId: number, tariffType: string) => void;
  isOpen: boolean;
  onToggle: () => void;
}

const TariffMenu = ({ user, onTariffChange, isOpen, onToggle }: TariffMenuProps) => {
  const tariffs = [
    { type: 'test', name: 'Тестовый' },
    { type: 'trial', name: 'Пробный' },
    { type: 'pro', name: 'Про' }
  ];

  return (
    <div className="relative">
      <button
        onClick={onToggle}
        className="p-2 rounded-md hover:bg-gray-100 transition-colors"
      >
        <MoreVertical className="h-4 w-4" />
      </button>
      
      {isOpen && (
        <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg border border-gray-200 z-10">
          <div className="py-1">
            <div className="px-4 py-2 text-sm font-medium text-gray-700 border-b">
              Изменить тариф
            </div>
            {tariffs.map((tariff) => (
              <button
                key={tariff.type}
                onClick={() => {
                  onTariffChange(user.id, tariff.type);
                  onToggle();
                }}
                className={`
                  block w-full text-left px-4 py-2 text-sm hover:bg-gray-100 transition-colors
                  ${user.tariff_type === tariff.type ? 'bg-blue-50 text-blue-700' : 'text-gray-700'}
                `}
              >
                {tariff.name}
                {user.tariff_type === tariff.type && (
                  <span className="ml-2 text-xs">(текущий)</span>
                )}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterTariff, setFilterTariff] = useState('all');
  const [openMenuId, setOpenMenuId] = useState<number | null>(null);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/v1/admin/users', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setUsers(data);
      } else {
        console.error('Ошибка загрузки пользователей');
      }
    } catch (error) {
      console.error('Ошибка загрузки пользователей:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleTariffChange = async (userId: number, tariffType: string) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/v1/admin/users/tariff', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          user_id: userId,
          tariff_type: tariffType
        })
      });

      if (response.ok) {
        // Обновляем список пользователей
        await fetchUsers();
      } else {
        console.error('Ошибка обновления тарифа');
      }
    } catch (error) {
      console.error('Ошибка обновления тарифа:', error);
    }
  };

  const filteredUsers = users.filter(user => {
    const matchesSearch = 
      user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (user.first_name && user.first_name.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (user.last_name && user.last_name.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesTariff = filterTariff === 'all' || user.tariff_type === filterTariff;
    
    return matchesSearch && matchesTariff;
  });

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ru-RU');
  };

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
        <h1 className="text-2xl font-bold text-gray-900">Пользователи</h1>
        <p className="mt-2 text-gray-600">
          Управление пользователями и их тарифными планами
        </p>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Поиск по имени или email..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
          <div className="sm:w-48">
            <div className="relative">
              <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <select
                value={filterTariff}
                onChange={(e) => setFilterTariff(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent appearance-none"
              >
                <option value="all">Все тарифы</option>
                <option value="test">Тестовый</option>
                <option value="trial">Пробный</option>
                <option value="pro">Про</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Users table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Фамилия
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Имя
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Email
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Дата регистрации
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Тариф
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Настройки
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredUsers.map((user) => (
                <tr key={user.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {user.last_name || '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {user.first_name || '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {user.email}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {formatDate(user.created_at)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {user.tariff_name ? (
                      <span className={`
                        inline-flex px-2 py-1 text-xs font-semibold rounded-full
                        ${user.tariff_type === 'test' ? 'bg-gray-100 text-gray-800' : ''}
                        ${user.tariff_type === 'trial' ? 'bg-yellow-100 text-yellow-800' : ''}
                        ${user.tariff_type === 'pro' ? 'bg-green-100 text-green-800' : ''}
                      `}>
                        {user.tariff_name}
                      </span>
                    ) : (
                      <span className="text-gray-400 text-sm">Не назначен</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <TariffMenu
                      user={user}
                      onTariffChange={handleTariffChange}
                      isOpen={openMenuId === user.id}
                      onToggle={() => setOpenMenuId(openMenuId === user.id ? null : user.id)}
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {filteredUsers.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500">Пользователи не найдены</p>
          </div>
        )}
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-2xl font-bold text-gray-900">{users.length}</div>
          <div className="text-sm text-gray-600">Всего пользователей</div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-2xl font-bold text-gray-900">
            {users.filter(u => u.is_active).length}
          </div>
          <div className="text-sm text-gray-600">Активных пользователей</div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-2xl font-bold text-gray-900">
            {users.filter(u => u.tariff_type === 'pro').length}
          </div>
          <div className="text-sm text-gray-600">Пользователей с тарифом &quot;Про&quot;</div>
        </div>
      </div>
    </div>
  );
}
