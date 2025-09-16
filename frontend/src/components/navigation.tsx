'use client';

import Link from 'next/link';
import { useAuth } from '@/lib/auth-context';
import { Button } from '@/components/ui/button';
import { useRouter, usePathname } from 'next/navigation';

export default function Navigation() {
  const { user, logout, isAuthenticated } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  const isActive = (path: string) => pathname === path;

  return (
    <nav className="bg-white shadow-sm border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <div className="flex-shrink-0 flex items-center">
              <Link href="/" className="text-2xl font-bold text-primary">
                Triplan
              </Link>
            </div>
            
            {isAuthenticated && (
              <div className="hidden sm:ml-8 sm:flex sm:space-x-8">
                <Link
                  href="/dashboard"
                  className={`inline-flex items-center px-1 pt-1 text-sm font-medium border-b-2 ${
                    isActive('/dashboard')
                      ? 'border-primary text-primary'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  Главная
                </Link>
                <Link
                  href="/plan"
                  className={`inline-flex items-center px-1 pt-1 text-sm font-medium border-b-2 ${
                    isActive('/plan')
                      ? 'border-primary text-primary'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  План
                </Link>
                <Link
                  href="/statistics"
                  className={`inline-flex items-center px-1 pt-1 text-sm font-medium border-b-2 ${
                    isActive('/statistics')
                      ? 'border-primary text-primary'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  Статистика
                </Link>
                <Link
                  href="/profile"
                  className={`inline-flex items-center px-1 pt-1 text-sm font-medium border-b-2 ${
                    isActive('/profile')
                      ? 'border-primary text-primary'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  Профиль
                </Link>
              </div>
            )}
          </div>

          <div className="flex items-center space-x-4">
            {isAuthenticated ? (
              <div className="flex items-center space-x-4">
                <span className="text-sm text-gray-700">
                  Привет, {user?.first_name || user?.email}!
                </span>
                <Button variant="outline" onClick={handleLogout}>
                  Выйти
                </Button>
              </div>
            ) : (
              <div className="flex items-center space-x-4">
                <Link href="/auth/login">
                  <Button variant="ghost">Войти</Button>
                </Link>
                <Link href="/auth/register">
                  <Button>Регистрация</Button>
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Мобильное меню */}
      {isAuthenticated && (
        <div className="sm:hidden border-t border-gray-200">
          <div className="pt-2 pb-3 space-y-1">
            <Link
              href="/dashboard"
              className={`block pl-3 pr-4 py-2 text-base font-medium ${
                isActive('/dashboard')
                  ? 'text-primary bg-primary/10 border-r-4 border-primary'
                  : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
              }`}
            >
              Главная
            </Link>
            <Link
              href="/plan"
              className={`block pl-3 pr-4 py-2 text-base font-medium ${
                isActive('/plan')
                  ? 'text-primary bg-primary/10 border-r-4 border-primary'
                  : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
              }`}
            >
              План
            </Link>
            <Link
              href="/statistics"
              className={`block pl-3 pr-4 py-2 text-base font-medium ${
                isActive('/statistics')
                  ? 'text-primary bg-primary/10 border-r-4 border-primary'
                  : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
              }`}
            >
              Статистика
            </Link>
            <Link
              href="/profile"
              className={`block pl-3 pr-4 py-2 text-base font-medium ${
                isActive('/profile')
                  ? 'text-primary bg-primary/10 border-r-4 border-primary'
                  : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
              }`}
            >
              Профиль
            </Link>
          </div>
        </div>
      )}
    </nav>
  );
}
