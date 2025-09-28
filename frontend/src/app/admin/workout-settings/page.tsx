'use client';

import { useEffect, useState } from 'react';
import { Save, Check, X, RotateCcw, Info } from 'lucide-react';

interface WorkoutCoefficients {
  id: number;
  // Коэффициенты для недельного километража
  weekly_distance_beginner: number;
  weekly_distance_5_10: number;
  weekly_distance_10_30: number;
  weekly_distance_30_50: number;
  weekly_distance_50_plus: number;
  
  // Коэффициенты для комфортного темпа
  pace_8_plus: number;
  pace_7_8: number;
  pace_6_7: number;
  pace_5_6: number;
  pace_4_5: number;
  pace_4_minus: number;
  
  // Коэффициенты для целевой дистанции
  target_distance_5k: number;
  target_distance_10k: number;
  target_distance_21k: number;
  target_distance_42k: number;
  
  // Коэффициенты для времени подготовки
  time_preparation_base: number;
  time_preparation_weeks_optimal: number;
  
  created_at: string;
  updated_at: string;
}

const defaultCoefficients: Omit<WorkoutCoefficients, 'id' | 'created_at' | 'updated_at'> = {
  weekly_distance_beginner: 10,
  weekly_distance_5_10: 50,
  weekly_distance_10_30: 100,
  weekly_distance_30_50: 200,
  weekly_distance_50_plus: 300,
  
  pace_8_plus: 20,
  pace_7_8: 50,
  pace_6_7: 100,
  pace_5_6: 150,
  pace_4_5: 200,
  pace_4_minus: 300,
  
  target_distance_5k: 50,
  target_distance_10k: 100,
  target_distance_21k: 150,
  target_distance_42k: 250,
  
  time_preparation_base: 100,
  time_preparation_weeks_optimal: 16
};

export default function WorkoutSettingsPage() {
  const [coefficients, setCoefficients] = useState<WorkoutCoefficients | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState<string | null>(null);

  useEffect(() => {
    fetchCoefficients();
  }, []);

  const fetchCoefficients = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/v1/admin/workout-coefficients', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setCoefficients(data);
      } else {
        console.error('Ошибка загрузки коэффициентов');
      }
    } catch (error) {
      console.error('Ошибка загрузки коэффициентов:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCoefficientChange = (field: keyof WorkoutCoefficients, value: number) => {
    if (coefficients) {
      setCoefficients({
        ...coefficients,
        [field]: value
      });
    }
  };

  const handleSave = async () => {
    if (!coefficients) return;

    setIsSaving(true);
    setSaveMessage(null);

    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/v1/admin/workout-coefficients', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          weekly_distance_beginner: coefficients.weekly_distance_beginner,
          weekly_distance_5_10: coefficients.weekly_distance_5_10,
          weekly_distance_10_30: coefficients.weekly_distance_10_30,
          weekly_distance_30_50: coefficients.weekly_distance_30_50,
          weekly_distance_50_plus: coefficients.weekly_distance_50_plus,
          
          pace_8_plus: coefficients.pace_8_plus,
          pace_7_8: coefficients.pace_7_8,
          pace_6_7: coefficients.pace_6_7,
          pace_5_6: coefficients.pace_5_6,
          pace_4_5: coefficients.pace_4_5,
          pace_4_minus: coefficients.pace_4_minus,
          
          target_distance_5k: coefficients.target_distance_5k,
          target_distance_10k: coefficients.target_distance_10k,
          target_distance_21k: coefficients.target_distance_21k,
          target_distance_42k: coefficients.target_distance_42k,
          
          time_preparation_base: coefficients.time_preparation_base,
          time_preparation_weeks_optimal: coefficients.time_preparation_weeks_optimal
        })
      });

      if (response.ok) {
        setSaveMessage('Коэффициенты тренировок успешно сохранены');
        await fetchCoefficients(); // Обновляем данные
      } else {
        setSaveMessage('Ошибка сохранения коэффициентов');
      }
    } catch (error) {
      console.error('Ошибка сохранения коэффициентов:', error);
      setSaveMessage('Ошибка сохранения коэффициентов');
    } finally {
      setIsSaving(false);
      // Убираем сообщение через 3 секунды
      setTimeout(() => setSaveMessage(null), 3000);
    }
  };

  const handleReset = () => {
    if (coefficients) {
      setCoefficients({
        ...coefficients,
        ...defaultCoefficients
      });
    }
  };

  const coefficientGroups = [
    {
      title: 'Коэффициенты для недельного километража',
      description: 'Влияют на сложность плана в зависимости от текущего недельного километража пользователя',
      fields: [
        { key: 'weekly_distance_beginner', label: 'Только начинаю бегать', min: 0, max: 1000 },
        { key: 'weekly_distance_5_10', label: '5-10 км в неделю', min: 0, max: 1000 },
        { key: 'weekly_distance_10_30', label: '10-30 км в неделю', min: 0, max: 1000 },
        { key: 'weekly_distance_30_50', label: '30-50 км в неделю', min: 0, max: 1000 },
        { key: 'weekly_distance_50_plus', label: 'Больше 50 км в неделю', min: 0, max: 1000 }
      ]
    },
    {
      title: 'Коэффициенты для комфортного темпа',
      description: 'Влияют на сложность плана в зависимости от комфортного темпа бега пользователя',
      fields: [
        { key: 'pace_8_plus', label: 'Медленнее 8 мин/км', min: 0, max: 1000 },
        { key: 'pace_7_8', label: '7-8 мин/км', min: 0, max: 1000 },
        { key: 'pace_6_7', label: '6-7 мин/км', min: 0, max: 1000 },
        { key: 'pace_5_6', label: '5-6 мин/км', min: 0, max: 1000 },
        { key: 'pace_4_5', label: '4-5 мин/км', min: 0, max: 1000 },
        { key: 'pace_4_minus', label: 'Быстрее 4 мин/км', min: 0, max: 1000 }
      ]
    },
    {
      title: 'Коэффициенты для целевой дистанции',
      description: 'Влияют на сложность плана в зависимости от целевой дистанции соревнования',
      fields: [
        { key: 'target_distance_5k', label: '5 км', min: 0, max: 1000 },
        { key: 'target_distance_10k', label: '10 км', min: 0, max: 1000 },
        { key: 'target_distance_21k', label: '21 км (полумарафон)', min: 0, max: 1000 },
        { key: 'target_distance_42k', label: '42 км (марафон)', min: 0, max: 1000 }
      ]
    },
    {
      title: 'Коэффициенты для времени подготовки',
      description: 'Влияют на сложность плана в зависимости от времени до соревнования',
      fields: [
        { key: 'time_preparation_base', label: 'Базовый коэффициент времени', min: 0, max: 1000 },
        { key: 'time_preparation_weeks_optimal', label: 'Оптимальное количество недель', min: 1, max: 52 }
      ]
    }
  ];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!coefficients) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Не удалось загрузить коэффициенты</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Настройки тренировок</h1>
        <p className="mt-2 text-gray-600">
          Редактирование коэффициентов для расчета сложности планов тренировок
        </p>
      </div>

      {/* Save message */}
      {saveMessage && (
        <div className={`
          p-4 rounded-md flex items-center
          ${saveMessage.includes('успешно') ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'}
        `}>
          {saveMessage.includes('успешно') ? (
            <Check className="h-5 w-5 mr-2" />
          ) : (
            <X className="h-5 w-5 mr-2" />
          )}
          {saveMessage}
        </div>
      )}

      {/* Info */}
      <div className="bg-blue-50 rounded-lg p-6">
        <div className="flex items-start">
          <Info className="h-5 w-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" />
          <div className="text-sm text-blue-800">
            <p className="font-medium mb-2">Как работают коэффициенты:</p>
            <ul className="space-y-1 list-disc list-inside">
              <li>Коэффициенты используются для расчета сложности плана тренировок (от 0 до 1000)</li>
              <li>Более высокие значения увеличивают сложность плана</li>
              <li>Изменения применяются ко всем новым планам, создаваемым после сохранения</li>
              <li>Существующие планы не изменяются</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Coefficient groups */}
      {coefficientGroups.map((group, groupIndex) => (
        <div key={groupIndex} className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-2">{group.title}</h3>
          <p className="text-sm text-gray-600 mb-4">{group.description}</p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {group.fields.map((field) => (
              <div key={field.key}>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {field.label}
                </label>
                <input
                  type="number"
                  min={field.min}
                  max={field.max}
                  value={coefficients[field.key as keyof WorkoutCoefficients] as number}
                  onChange={(e) => handleCoefficientChange(
                    field.key as keyof WorkoutCoefficients,
                    parseInt(e.target.value) || 0
                  )}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            ))}
          </div>
        </div>
      ))}

      {/* Action buttons */}
      <div className="flex justify-between">
        <button
          onClick={handleReset}
          className="flex items-center px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors"
        >
          <RotateCcw className="h-4 w-4 mr-2" />
          Сбросить к значениям по умолчанию
        </button>

        <button
          onClick={handleSave}
          disabled={isSaving}
          className="flex items-center px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {isSaving ? (
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
          ) : (
            <Save className="h-4 w-4 mr-2" />
          )}
          {isSaving ? 'Сохранение...' : 'Сохранить коэффициенты'}
        </button>
      </div>

      {/* Last updated info */}
      {coefficients.updated_at && (
        <div className="text-sm text-gray-500 text-center">
          Последнее обновление: {new Date(coefficients.updated_at).toLocaleString('ru-RU')}
        </div>
      )}
    </div>
  );
}
