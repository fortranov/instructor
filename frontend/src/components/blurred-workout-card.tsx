'use client';

import { Workout } from '@/types/api';
import { formatDuration, getSportIcon, getSportColor, getWorkoutTypeLabel, getWorkoutTypeColor } from '@/lib/utils';
import { Lock } from 'lucide-react';

interface BlurredWorkoutCardProps {
  workout: Workout;
}

export default function BlurredWorkoutCard({ workout }: BlurredWorkoutCardProps) {
  return (
    <div
      className="relative text-xs p-1 rounded border shadow-sm overflow-hidden select-none"
      style={{
        userSelect: 'none',
        WebkitUserSelect: 'none',
        WebkitTouchCallout: 'none',
        opacity: 0.5,
        filter: 'blur(2px)',
        pointerEvents: 'none',
        backgroundColor: '#f9fafb',
        borderColor: '#e5e7eb',
      }}
      title="Тренировка недоступна на вашем тарифе"
    >
      {/* Иконка замка */}
      <div className="absolute inset-0 flex items-center justify-center z-10 bg-gray-900 bg-opacity-5">
        <Lock className="w-4 h-4 text-gray-400" style={{ filter: 'blur(0px)' }} />
      </div>

      {/* Содержимое карточки (замыленное) */}
      <div className="relative z-0">
        <div className="flex items-center gap-1 mb-1">
          <span className="text-sm">{getSportIcon(workout.sport_type)}</span>
          <span className={`
            inline-block w-2 h-2 rounded-full flex-shrink-0
            ${getSportColor(workout.sport_type)}
          `}></span>
        </div>
        
        <div className="text-xs text-gray-600 truncate">
          {formatDuration(workout.duration_minutes)}
        </div>
        
        <div className={`
          text-xs px-1 py-0.5 rounded text-center truncate
          ${getWorkoutTypeColor(workout.workout_type)}
        `}>
          {getWorkoutTypeLabel(workout.workout_type)}
        </div>
      </div>
    </div>
  );
}

