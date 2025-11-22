'use client';

import { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { SportType, WorkoutType } from '@/types/api';
import { getSportLabel, getWorkoutTypeLabel } from '@/lib/utils';

interface CustomWorkoutModalProps {
  date: string; // ISO date string
  isOpen: boolean;
  onClose: () => void;
  onSave: (sportType: SportType, durationMinutes: number, workoutType: WorkoutType) => Promise<void>;
}

export default function CustomWorkoutModal({ date, isOpen, onClose, onSave }: CustomWorkoutModalProps) {
  const [sportType, setSportType] = useState<SportType>(SportType.RUNNING);
  const [hours, setHours] = useState<number>(0);
  const [minutes, setMinutes] = useState<number>(30);
  const [workoutType, setWorkoutType] = useState<WorkoutType>(WorkoutType.ENDURANCE);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    if (!isOpen) {
      // Сбросить форму при закрытии
      setSportType(SportType.RUNNING);
      setHours(0);
      setMinutes(30);
      setWorkoutType(WorkoutType.ENDURANCE);
      setError('');
    }
  }, [isOpen]);

  const handleSave = async () => {
    const totalMinutes = hours * 60 + minutes;

    if (totalMinutes === 0) {
      setError('Длительность должна быть больше 0');
      return;
    }

    if (totalMinutes > 600) {
      setError('Длительность не должна превышать 10 часов');
      return;
    }

    setError('');
    setIsSaving(true);

    try {
      await onSave(sportType, totalMinutes, workoutType);
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка при сохранении');
    } finally {
      setIsSaving(false);
    }
  };

  if (!isOpen) return null;

  const formatDate = (dateStr: string) => {
    const d = new Date(dateStr);
    return d.toLocaleDateString('ru-RU', {
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 p-4">
      <Card className="w-full max-w-md max-h-[90vh] overflow-y-auto">
        <CardHeader className="relative">
          <button
            onClick={onClose}
            className="absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:pointer-events-none"
          >
            <X className="h-5 w-5" />
            <span className="sr-only">Закрыть</span>
          </button>
          <CardTitle className="text-xl font-semibold">
            Добавить тренировку
          </CardTitle>
          <p className="text-sm text-muted-foreground mt-1">
            {formatDate(date)}
          </p>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Выбор вида спорта */}
          <div>
            <label htmlFor="sport-type" className="block text-sm font-medium mb-2">
              Вид спорта
            </label>
            <select
              id="sport-type"
              value={sportType}
              onChange={(e) => setSportType(e.target.value as SportType)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value={SportType.RUNNING}>{getSportLabel(SportType.RUNNING)}</option>
              <option value={SportType.CYCLING}>{getSportLabel(SportType.CYCLING)}</option>
              <option value={SportType.SWIMMING}>{getSportLabel(SportType.SWIMMING)}</option>
              <option value={SportType.STRENGTH}>{getSportLabel(SportType.STRENGTH)}</option>
            </select>
          </div>

          {/* Длительность */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Длительность
            </label>
            <div className="flex gap-4">
              <div className="flex-1">
                <label htmlFor="hours" className="block text-xs text-gray-600 mb-1">
                  Часы
                </label>
                <input
                  id="hours"
                  type="number"
                  min="0"
                  max="10"
                  value={hours}
                  onChange={(e) => setHours(Math.max(0, Math.min(10, parseInt(e.target.value) || 0)))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div className="flex-1">
                <label htmlFor="minutes" className="block text-xs text-gray-600 mb-1">
                  Минуты
                </label>
                <input
                  id="minutes"
                  type="number"
                  min="0"
                  max="59"
                  value={minutes}
                  onChange={(e) => setMinutes(Math.max(0, Math.min(59, parseInt(e.target.value) || 0)))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          </div>

          {/* Тип тренировки */}
          <div>
            <label htmlFor="workout-type" className="block text-sm font-medium mb-2">
              Тип тренировки
            </label>
            <select
              id="workout-type"
              value={workoutType}
              onChange={(e) => setWorkoutType(e.target.value as WorkoutType)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value={WorkoutType.ENDURANCE}>{getWorkoutTypeLabel(WorkoutType.ENDURANCE)}</option>
              <option value={WorkoutType.INTERVAL}>{getWorkoutTypeLabel(WorkoutType.INTERVAL)}</option>
              <option value={WorkoutType.RECOVERY}>{getWorkoutTypeLabel(WorkoutType.RECOVERY)}</option>
            </select>
          </div>

          {/* Ошибка */}
          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-md text-sm text-red-600">
              {error}
            </div>
          )}

          {/* Кнопки */}
          <div className="flex gap-3 pt-4">
            <Button
              variant="outline"
              onClick={onClose}
              disabled={isSaving}
              className="flex-1"
            >
              Отмена
            </Button>
            <Button
              onClick={handleSave}
              disabled={isSaving}
              className="flex-1"
            >
              {isSaving ? 'Сохранение...' : 'Сохранить'}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
