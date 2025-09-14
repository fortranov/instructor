import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"
import { format, parseISO, startOfMonth, endOfMonth, eachDayOfInterval, isSameMonth, isSameDay } from 'date-fns';
import { ru } from 'date-fns/locale';
import { SportType, WorkoutType, CompetitionType } from '@/types/api';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// Утилиты для работы с датами
export const formatDate = (date: Date | string, formatStr: string = 'dd.MM.yyyy'): string => {
  const dateObj = typeof date === 'string' ? parseISO(date) : date;
  return format(dateObj, formatStr, { locale: ru });
};

export const formatDateISO = (date: Date): string => {
  return format(date, 'yyyy-MM-dd');
};

export const parseDate = (dateString: string): Date => {
  return parseISO(dateString);
};

export const getMonthDays = (date: Date): Date[] => {
  const start = startOfMonth(date);
  const end = endOfMonth(date);
  return eachDayOfInterval({ start, end });
};

export const isSameDateMonth = (date1: Date, date2: Date): boolean => {
  return isSameMonth(date1, date2);
};

export const isSameDateDay = (date1: Date, date2: Date): boolean => {
  return isSameDay(date1, date2);
};

// Утилиты для форматирования времени тренировок
export const formatDuration = (minutes: number): string => {
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  
  if (hours === 0) {
    return `${mins}мин`;
  }
  
  if (mins === 0) {
    return `${hours}ч`;
  }
  
  return `${hours}ч ${mins}мин`;
};

// Утилиты для получения иконок и цветов спорта
export const getSportIcon = (sportType: SportType): string => {
  switch (sportType) {
    case SportType.RUNNING:
      return '🏃';
    case SportType.CYCLING:
      return '🚴';
    case SportType.SWIMMING:
      return '🏊';
    default:
      return '🏃';
  }
};

export const getSportColor = (sportType: SportType): string => {
  switch (sportType) {
    case SportType.RUNNING:
      return 'bg-red-500';
    case SportType.CYCLING:
      return 'bg-blue-500';
    case SportType.SWIMMING:
      return 'bg-cyan-500';
    default:
      return 'bg-gray-500';
  }
};

export const getWorkoutTypeLabel = (workoutType: WorkoutType): string => {
  switch (workoutType) {
    case WorkoutType.ENDURANCE:
      return 'Длительная';
    case WorkoutType.INTERVAL:
      return 'Интервальная';
    case WorkoutType.RECOVERY:
      return 'Восстанавливающая';
    default:
      return workoutType;
  }
};

export const getWorkoutTypeColor = (workoutType: WorkoutType): string => {
  switch (workoutType) {
    case WorkoutType.ENDURANCE:
      return 'bg-green-100 text-green-800';
    case WorkoutType.INTERVAL:
      return 'bg-orange-100 text-orange-800';
    case WorkoutType.RECOVERY:
      return 'bg-blue-100 text-blue-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

export const getCompetitionTypeLabel = (competitionType: CompetitionType): string => {
  switch (competitionType) {
    case CompetitionType.RUN_10K:
      return '10 километров';
    case CompetitionType.RUN_HALF_MARATHON:
      return 'Полумарафон';
    case CompetitionType.RUN_MARATHON:
      return 'Марафон';
    case CompetitionType.CYCLING:
      return 'Велосипед';
    case CompetitionType.SWIMMING:
      return 'Плавание';
    case CompetitionType.TRIATHLON_SPRINT:
      return 'Триатлон спринт';
    case CompetitionType.TRIATHLON_OLYMPIC:
      return 'Триатлон олимпийская дистанция';
    case CompetitionType.TRIATHLON_IRONMAN:
      return 'Триатлон железная дистанция';
    default:
      return competitionType;
  }
};

// Утилиты для валидации
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const isValidPassword = (password: string): boolean => {
  return password.length >= 6;
};

// Утилиты для работы с ошибками
export const getErrorMessage = (error: unknown): string => {
  if (error instanceof Error) {
    return error.message;
  }
  
  if (typeof error === 'string') {
    return error;
  }
  
  return 'Произошла неизвестная ошибка';
};
