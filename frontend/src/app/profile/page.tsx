'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth-context';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import Navigation from '@/components/navigation';
import apiClient from '@/lib/api';
import { CompetitionType, CompetitionTypesResponse } from '@/types/api';
import { getErrorMessage, isValidEmail, isValidPassword } from '@/lib/utils';

export default function ProfilePage() {
  const { user, isAuthenticated, loading: authLoading, updateUser } = useAuth();
  const router = useRouter();

  // Данные пользователя
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  // Данные плана тренировок
  const [complexity, setComplexity] = useState(500);
  const [competitionDate, setCompetitionDate] = useState('');
  const [competitionType, setCompetitionType] = useState<CompetitionType>(CompetitionType.RUN_10K);
  const [competitionDistance, setCompetitionDistance] = useState('');

  // Справочные данные
  const [competitionTypes, setCompetitionTypes] = useState<CompetitionTypesResponse | null>(null);

  // Состояния
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/auth/login');
    }
  }, [isAuthenticated, authLoading, router]);

  useEffect(() => {
    if (user) {
      setFirstName(user.first_name || '');
      setLastName(user.last_name || '');
      setEmail(user.email);
    }
  }, [user]);

  useEffect(() => {
    const loadCompetitionTypes = async () => {
      try {
        const types = await apiClient.getCompetitionTypes();
        setCompetitionTypes(types);
      } catch (err) {
        console.error('Ошибка загрузки типов соревнований:', getErrorMessage(err));
      }
    };

    loadCompetitionTypes();
  }, []);

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!isValidEmail(email)) {
      setError('Введите корректный email адрес');
      return;
    }

    if (newPassword && !isValidPassword(newPassword)) {
      setError('Новый пароль должен содержать минимум 6 символов');
      return;
    }

    if (newPassword && newPassword !== confirmPassword) {
      setError('Пароли не совпадают');
      return;
    }

    if ((newPassword || email !== user?.email) && !currentPassword) {
      setError('Введите текущий пароль для изменения email или пароля');
      return;
    }

    setLoading(true);

    try {
      const updateData: Record<string, string | undefined> = {
        first_name: firstName || undefined,
        last_name: lastName || undefined,
      };

      if (email !== user?.email) {
        updateData.email = email;
        updateData.current_password = currentPassword;
      }

      if (newPassword) {
        updateData.new_password = newPassword;
        updateData.current_password = currentPassword;
      }

      const updatedUser = await apiClient.updateCurrentUser(updateData);
      updateUser(updatedUser);
      
      setSuccess('Профиль успешно обновлен');
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const handleCreatePlan = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!user?.uin) {
      setError('Ошибка: не удается определить пользователя');
      return;
    }

    if (!competitionDate) {
      setError('Выберите дату соревнования');
      return;
    }

    const selectedDate = new Date(competitionDate);
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    if (selectedDate <= today) {
      setError('Дата соревнования должна быть в будущем');
      return;
    }

    if ((competitionType === CompetitionType.CYCLING || competitionType === CompetitionType.SWIMMING) && !competitionDistance) {
      setError('Укажите дистанцию для выбранного типа соревнования');
      return;
    }

    setLoading(true);

    try {
      const planData = {
        uin: user.uin,
        complexity,
        competition_date: competitionDate,
        competition_type: competitionType,
        competition_distance: competitionDistance ? parseFloat(competitionDistance) : undefined,
      };

      await apiClient.createTrainingPlan(planData);
      setSuccess('План тренировок успешно создан! Перейдите в раздел "План" для просмотра.');
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const needsDistance = competitionType === CompetitionType.CYCLING || competitionType === CompetitionType.SWIMMING;

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
      
      <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Профиль</h1>
          <p className="text-gray-600 mt-2">
            Управляйте своими данными и настройками планов тренировок
          </p>
        </div>

        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-md">
            {error}
          </div>
        )}

        {success && (
          <div className="mb-6 bg-green-50 border border-green-200 text-green-600 px-4 py-3 rounded-md">
            {success}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Личные данные */}
          <Card>
            <CardHeader>
              <CardTitle>Личные данные</CardTitle>
              <CardDescription>
                Обновите свою персональную информацию
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleUpdateProfile} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="firstName" className="block text-sm font-medium text-gray-700 mb-1">
                      Имя
                    </label>
                    <Input
                      id="firstName"
                      value={firstName}
                      onChange={(e) => setFirstName(e.target.value)}
                      placeholder="Ваше имя"
                    />
                  </div>
                  <div>
                    <label htmlFor="lastName" className="block text-sm font-medium text-gray-700 mb-1">
                      Фамилия
                    </label>
                    <Input
                      id="lastName"
                      value={lastName}
                      onChange={(e) => setLastName(e.target.value)}
                      placeholder="Ваша фамилия"
                    />
                  </div>
                </div>

                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                    Email
                  </label>
                  <Input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="your@email.com"
                  />
                </div>

                <div>
                  <label htmlFor="currentPassword" className="block text-sm font-medium text-gray-700 mb-1">
                    Текущий пароль
                  </label>
                  <Input
                    id="currentPassword"
                    type="password"
                    value={currentPassword}
                    onChange={(e) => setCurrentPassword(e.target.value)}
                    placeholder="Введите для изменения email или пароля"
                  />
                </div>

                <div>
                  <label htmlFor="newPassword" className="block text-sm font-medium text-gray-700 mb-1">
                    Новый пароль
                  </label>
                  <Input
                    id="newPassword"
                    type="password"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    placeholder="Оставьте пустым, если не хотите менять"
                  />
                </div>

                {newPassword && (
                  <div>
                    <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-1">
                      Подтвердите новый пароль
                    </label>
                    <Input
                      id="confirmPassword"
                      type="password"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      placeholder="Повторите новый пароль"
                    />
                  </div>
                )}

                <Button type="submit" disabled={loading}>
                  {loading ? 'Сохранение...' : 'Сохранить изменения'}
                </Button>
              </form>
            </CardContent>
          </Card>

          {/* Настройки плана тренировок */}
          <Card>
            <CardHeader>
              <CardTitle>План тренировок</CardTitle>
              <CardDescription>
                Создайте или обновите свой план тренировок
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleCreatePlan} className="space-y-4">
                <div>
                  <label htmlFor="complexity" className="block text-sm font-medium text-gray-700 mb-1">
                    Уровень сложности: {complexity}
                  </label>
                  <input
                    id="complexity"
                    type="range"
                    min="0"
                    max="1000"
                    step="50"
                    value={complexity}
                    onChange={(e) => setComplexity(parseInt(e.target.value))}
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>Начинающий (0)</span>
                    <span>Профессионал (1000)</span>
                  </div>
                </div>

                <div>
                  <label htmlFor="competitionDate" className="block text-sm font-medium text-gray-700 mb-1">
                    Дата соревнования
                  </label>
                  <Input
                    id="competitionDate"
                    type="date"
                    value={competitionDate}
                    onChange={(e) => setCompetitionDate(e.target.value)}
                    min={new Date().toISOString().split('T')[0]}
                  />
                </div>

                <div>
                  <label htmlFor="competitionType" className="block text-sm font-medium text-gray-700 mb-1">
                    Тип соревнования
                  </label>
                  <select
                    id="competitionType"
                    value={competitionType}
                    onChange={(e) => setCompetitionType(e.target.value as CompetitionType)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    {competitionTypes && (
                      <>
                        <optgroup label="Бег">
                          {competitionTypes.running.map(type => (
                            <option key={type.value} value={type.value}>
                              {type.label}
                            </option>
                          ))}
                        </optgroup>
                        <optgroup label="Велосипед">
                          {competitionTypes.cycling.map(type => (
                            <option key={type.value} value={type.value}>
                              {type.label}
                            </option>
                          ))}
                        </optgroup>
                        <optgroup label="Плавание">
                          {competitionTypes.swimming.map(type => (
                            <option key={type.value} value={type.value}>
                              {type.label}
                            </option>
                          ))}
                        </optgroup>
                        <optgroup label="Триатлон">
                          {competitionTypes.triathlon.map(type => (
                            <option key={type.value} value={type.value}>
                              {type.label}
                            </option>
                          ))}
                        </optgroup>
                      </>
                    )}
                  </select>
                </div>

                {needsDistance && (
                  <div>
                    <label htmlFor="competitionDistance" className="block text-sm font-medium text-gray-700 mb-1">
                      Дистанция {competitionType === CompetitionType.CYCLING ? '(км)' : '(метры)'}
                    </label>
                    <Input
                      id="competitionDistance"
                      type="number"
                      step="0.1"
                      min="0.1"
                      value={competitionDistance}
                      onChange={(e) => setCompetitionDistance(e.target.value)}
                      placeholder={competitionType === CompetitionType.CYCLING ? 'Например: 40' : 'Например: 1500'}
                    />
                  </div>
                )}

                <Button type="submit" disabled={loading} className="w-full">
                  {loading ? 'Создание плана...' : 'Создать план тренировок'}
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
