'use client';

import { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Workout, SportType, WorkoutType } from '@/types/api';
import { getSportIcon, getSportLabel, getWorkoutTypeLabel, formatDuration } from '@/lib/utils';

interface WorkoutStage {
  duration: number; // в минутах
  description: string;
}

interface WorkoutModalProps {
  workout: Workout | null;
  isOpen: boolean;
  onClose: () => void;
}

export default function WorkoutModal({ workout, isOpen, onClose }: WorkoutModalProps) {
  const [stages, setStages] = useState<WorkoutStage[]>([]);

  useEffect(() => {
    if (workout) {
      const generatedStages = generateWorkoutStages(workout);
      setStages(generatedStages);
    }
  }, [workout]);

  const getActivityName = (sportType: SportType): string => {
    switch (sportType) {
      case SportType.RUNNING:
        return 'бег';
      case SportType.CYCLING:
        return 'езда на велосипеде';
      case SportType.SWIMMING:
        return 'плавание';
      default:
        return 'активность';
    }
  };

  const generateWorkoutStages = (workout: Workout): WorkoutStage[] => {
    const stages: WorkoutStage[] = [];
    const totalDuration = workout.duration_minutes;
    const activityName = getActivityName(workout.sport_type);
    
    // Разминка - всегда 5 минут
    stages.push({
      duration: 5,
      description: `Разминка - легкий ${activityName} для подготовки организма к нагрузке`
    });

    // Основная часть тренировки
    const mainDuration = totalDuration - 10; // вычитаем разминку и заминку
    
    if (workout.workout_type === WorkoutType.ENDURANCE) {
      // Длительная тренировка - равномерный бег во второй зоне
      stages.push({
        duration: mainDuration,
        description: `Равномерный ${activityName} во второй зоне интенсивности (комфортная скорость, можно поддерживать разговор)`
      });
    } else if (workout.workout_type === WorkoutType.RECOVERY) {
      // Восстановительная тренировка - равномерный бег в первой зоне
      stages.push({
        duration: mainDuration,
        description: `Восстановительный ${activityName} в первой зоне интенсивности (очень легкий темп, полное восстановление)`
      });
    } else if (workout.workout_type === WorkoutType.INTERVAL) {
      // Интервальная тренировка
      const intervals = generateIntervals(mainDuration, workout.sport_type);
      stages.push(...intervals);
    }

    // Заминка - всегда 5 минут
    stages.push({
      duration: 5,
      description: `Заминка - легкий ${activityName} для восстановления и снижения пульса`
    });

    return stages;
  };

  const generateIntervals = (totalDuration: number, sportType: SportType): WorkoutStage[] => {
    const intervals: WorkoutStage[] = [];
    const activityName = getActivityName(sportType);
    
    // Определяем длительность интервалов в зависимости от вида спорта
    let intervalDuration: number;
    let restDuration: number;
    
    switch (sportType) {
      case SportType.RUNNING:
        intervalDuration = 3; // 3 минуты ускорения
        restDuration = 2; // 2 минуты отдыха
        break;
      case SportType.CYCLING:
        intervalDuration = 4; // 4 минуты ускорения
        restDuration = 2; // 2 минуты отдыха
        break;
      case SportType.SWIMMING:
        intervalDuration = 2; // 2 минуты ускорения
        restDuration = 1; // 1 минута отдыха
        break;
      default:
        intervalDuration = 3;
        restDuration = 2;
    }

    const cycleDuration = intervalDuration + restDuration;
    const cycles = Math.floor(totalDuration / cycleDuration);
    const remainingTime = totalDuration - (cycles * cycleDuration);

    // Добавляем интервалы
    for (let i = 0; i < cycles; i++) {
      intervals.push({
        duration: intervalDuration,
        description: `Ускорение - высокий темп (4-5 зона интенсивности)`
      });
      
      if (i < cycles - 1 || remainingTime > 0) {
        intervals.push({
          duration: restDuration,
          description: `Медленный ${activityName} для восстановления`
        });
      }
    }

    // Добавляем оставшееся время как дополнительный интервал или отдых
    if (remainingTime > 0) {
      if (remainingTime >= intervalDuration) {
        intervals.push({
          duration: intervalDuration,
          description: `Ускорение - высокий темп (4-5 зона интенсивности)`
        });
        const finalRest = remainingTime - intervalDuration;
        if (finalRest > 0) {
          intervals.push({
            duration: finalRest,
            description: `Медленный ${activityName} для восстановления`
          });
        }
      } else {
        intervals.push({
          duration: remainingTime,
          description: `Медленный ${activityName} для восстановления`
        });
      }
    }

    return intervals;
  };

  if (!isOpen || !workout) {
    return null;
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
          <CardTitle className="text-xl font-semibold">
            Описание тренировки
          </CardTitle>
          <Button
            variant="ghost"
            size="sm"
            onClick={onClose}
            className="h-8 w-8 p-0"
          >
            <X className="h-4 w-4" />
          </Button>
        </CardHeader>
        
        <CardContent className="space-y-6">
          {/* Основная информация о тренировке */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 bg-gray-50 rounded-lg">
            <div className="text-center">
              <div className="flex items-center justify-center gap-2 mb-2">
                <span className="text-2xl">{getSportIcon(workout.sport_type)}</span>
                <span className="text-sm text-gray-600">{getSportLabel(workout.sport_type)}</span>
              </div>
            </div>
            
            <div className="text-center">
              <div className="text-lg font-semibold text-gray-900">
                {formatDuration(workout.duration_minutes)}
              </div>
              <div className="text-sm text-gray-600">Общее время</div>
            </div>
            
            <div className="text-center">
              <div className="text-lg font-semibold text-gray-900">
                {getWorkoutTypeLabel(workout.workout_type)}
              </div>
              <div className="text-sm text-gray-600">Тип тренировки</div>
            </div>
          </div>

          {/* Таблица этапов тренировки */}
          <div>
            <h3 className="text-lg font-semibold mb-4">План тренировки</h3>
            <div className="overflow-x-auto">
              <table className="w-full border-collapse border border-gray-300">
                <thead>
                  <tr className="bg-gray-100">
                    <th className="border border-gray-300 px-4 py-2 text-left font-semibold">
                      Длительность
                    </th>
                    <th className="border border-gray-300 px-4 py-2 text-left font-semibold">
                      Описание этапа
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {stages.map((stage, index) => (
                    <tr key={index} className="hover:bg-gray-50">
                      <td className="border border-gray-300 px-4 py-2 font-medium">
                        {formatDuration(stage.duration)}
                      </td>
                      <td className="border border-gray-300 px-4 py-2">
                        {stage.description}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Дополнительная информация */}
          <div className="p-4 bg-blue-50 rounded-lg">
            <h4 className="font-semibold text-blue-900 mb-2">Полезные советы:</h4>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• Следите за пульсом во время тренировки</li>
              <li>• Пейте воду до, во время и после тренировки</li>
              <li>• Не забывайте о правильной технике выполнения</li>
              <li>• При плохом самочувствии снизьте интенсивность</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
