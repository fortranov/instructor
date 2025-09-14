'use client';

import { useAuth } from '@/lib/auth-context';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import Navigation from '@/components/navigation';

export default function Home() {
  const { isAuthenticated } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (isAuthenticated) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, router]);

  if (isAuthenticated) {
    return null; // Будет перенаправлен на dashboard
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <Navigation />
      
      {/* Hero Section */}
      <section className="relative py-20 px-4">
        <div className="max-w-7xl mx-auto text-center">
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
            Персональные планы тренировок для{' '}
            <span className="text-blue-600">триатлона</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Создавайте индивидуальные планы тренировок по бегу, велосипеду, плаванию и триатлону. 
            Основано на методике Джо Фрила с учетом периодизации и вашего уровня подготовки.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/auth/register">
              <Button size="lg" className="text-lg px-8 py-3">
                Начать бесплатно
              </Button>
            </Link>
            <Link href="/auth/login">
              <Button variant="outline" size="lg" className="text-lg px-8 py-3">
                Войти в аккаунт
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4 bg-white">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
            Почему выбирают Triplan?
          </h2>
          
          <div className="grid md:grid-cols-3 gap-8">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <span className="text-2xl">🏃</span>
                  Персонализация
                </CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription>
                  Планы создаются с учетом вашего уровня сложности, целей и даты соревнований. 
                  Каждая тренировка адаптирована под ваши потребности.
                </CardDescription>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <span className="text-2xl">📊</span>
                  Научный подход
                </CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription>
                  Основано на методике Джо Фрила - признанного эксперта в области тренировок на выносливость. 
                  Используем принципы периодизации и прогрессивной нагрузки.
                </CardDescription>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <span className="text-2xl">🎯</span>
                  Удобное планирование
                </CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription>
                  Интуитивный календарь тренировок с детальной информацией о каждой сессии. 
                  Легко отслеживайте прогресс и корректируйте планы.
                </CardDescription>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Sports Images Section */}
      <section className="py-20 px-4 bg-gray-50">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
            Поддерживаемые виды спорта
          </h2>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="w-24 h-24 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-4xl">🏃‍♂️</span>
              </div>
              <h3 className="text-xl font-semibold mb-2">Бег</h3>
              <p className="text-gray-600">10км, полумарафон, марафон</p>
            </div>

            <div className="text-center">
              <div className="w-24 h-24 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-4xl">🚴‍♂️</span>
              </div>
              <h3 className="text-xl font-semibold mb-2">Велосипед</h3>
              <p className="text-gray-600">Любые дистанции</p>
            </div>

            <div className="text-center">
              <div className="w-24 h-24 bg-cyan-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-4xl">🏊‍♂️</span>
              </div>
              <h3 className="text-xl font-semibold mb-2">Плавание</h3>
              <p className="text-gray-600">Открытая вода и бассейн</p>
            </div>

            <div className="text-center">
              <div className="w-24 h-24 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-4xl">🏆</span>
              </div>
              <h3 className="text-xl font-semibold mb-2">Триатлон</h3>
              <p className="text-gray-600">Спринт, олимпийская, железная дистанция</p>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="py-20 px-4 bg-white">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
            Простые и честные цены
          </h2>
          
          <div className="grid md:grid-cols-2 gap-8">
            <Card className="relative">
              <CardHeader>
                <CardTitle>Базовый</CardTitle>
                <div className="text-3xl font-bold">Бесплатно</div>
                <CardDescription>Для начинающих спортсменов</CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 mb-6">
                  <li className="flex items-center gap-2">
                    <span className="text-green-500">✓</span>
                    1 план тренировок
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="text-green-500">✓</span>
                    Базовые типы тренировок
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="text-green-500">✓</span>
                    Календарь тренировок
                  </li>
                </ul>
                <Link href="/auth/register">
                  <Button className="w-full">Начать бесплатно</Button>
                </Link>
              </CardContent>
            </Card>

            <Card className="relative border-blue-200 shadow-lg">
              <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                <span className="bg-blue-500 text-white px-3 py-1 rounded-full text-sm">
                  Рекомендуем
                </span>
              </div>
              <CardHeader>
                <CardTitle>Премиум</CardTitle>
                <div className="text-3xl font-bold">₽990 <span className="text-lg font-normal text-gray-500">/мес</span></div>
                <CardDescription>Для серьезных спортсменов</CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 mb-6">
                  <li className="flex items-center gap-2">
                    <span className="text-green-500">✓</span>
                    Неограниченное количество планов
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="text-green-500">✓</span>
                    Все типы тренировок
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="text-green-500">✓</span>
                    Детальная аналитика
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="text-green-500">✓</span>
                    Поддержка тренера
                  </li>
                </ul>
                <Link href="/auth/register">
                  <Button className="w-full">Попробовать 7 дней бесплатно</Button>
                </Link>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12 px-4">
        <div className="max-w-7xl mx-auto text-center">
          <div className="mb-8">
            <h3 className="text-2xl font-bold mb-2">Triplan</h3>
            <p className="text-gray-400">Персональные планы тренировок для достижения ваших спортивных целей</p>
          </div>
          
          <div className="border-t border-gray-800 pt-8">
            <p className="text-gray-400">
              © 2024 Triplan. Все права защищены.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}