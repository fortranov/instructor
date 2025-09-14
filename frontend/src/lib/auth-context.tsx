'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User, UserLogin, UserRegistration } from '@/types/api';
import apiClient from '@/lib/api';
import { getErrorMessage } from '@/lib/utils';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (userData: UserLogin) => Promise<void>;
  register: (userData: UserRegistration) => Promise<void>;
  logout: () => void;
  updateUser: (userData: Partial<User>) => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      try {
        if (apiClient.isAuthenticated()) {
          const currentUser = await apiClient.getCurrentUser();
          setUser(currentUser);
        }
      } catch (error) {
        console.error('Ошибка при инициализации аутентификации:', getErrorMessage(error));
        apiClient.removeToken();
      } finally {
        setLoading(false);
      }
    };

    initAuth();
  }, []);

  const login = async (userData: UserLogin) => {
    try {
      const tokenData = await apiClient.login(userData);
      setUser(tokenData.user);
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  };

  const register = async (userData: UserRegistration) => {
    try {
      await apiClient.register(userData);
      // После регистрации автоматически входим
      await login({ email: userData.email, password: userData.password });
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  };

  const logout = () => {
    apiClient.removeToken();
    setUser(null);
  };

  const updateUser = (userData: Partial<User>) => {
    if (user) {
      setUser({ ...user, ...userData });
    }
  };

  const value: AuthContextType = {
    user,
    loading,
    login,
    register,
    logout,
    updateUser,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
