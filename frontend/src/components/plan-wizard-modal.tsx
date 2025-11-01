'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { X, ChevronLeft, ChevronRight } from 'lucide-react';
import apiClient from '@/lib/api';
import { CompetitionTypesResponse } from '@/types/api';

export interface PlanWizardData {
  sportType?: string;
  weeklyDistance: string;
  comfortablePace: string;
  targetDistance: string;
  competitionDate: string;
  hasSpecificGoal: boolean;
  hasStrengthTraining: boolean;
  preferredWorkoutDays: number[];
}

interface PlanWizardModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: PlanWizardData) => Promise<void>;
  loading?: boolean;
  initialPreferredDays?: number[];
}

const WEEKLY_DISTANCE_OPTIONS_RUNNING = [
  { value: 'beginner', label: 'Только начинаю бегать' },
  { value: '5-10', label: '5-10 км' },
  { value: '10-30', label: '10-30 км' },
  { value: '30-50', label: '30-50 км' },
  { value: '50+', label: 'Больше 50 км' },
];

const WEEKLY_DISTANCE_OPTIONS_SWIMMING = [
  { value: 'beginner', label: 'Только начинаю' },
  { value: '50-500', label: '50-500 метров' },
  { value: '500-1000', label: '500-1000 метров' },
  { value: '1000-3000', label: '1000-3000 метров' },
  { value: '3000+', label: 'Более 3000 метров' },
];

const WEEKLY_DISTANCE_OPTIONS_CYCLING = [
  { value: 'beginner', label: 'Только начинаю' },
  { value: '1-10', label: '1-10 км' },
  { value: '10-50', label: '10-50 км' },
  { value: '50-200', label: '50-200 км' },
  { value: '200+', label: 'Более 200 км' },
];

const PACE_OPTIONS = [
  { value: '8+', label: 'Медленнее 8 мин/км' },
  { value: '7-8', label: '7-8 мин/км' },
  { value: '6-7', label: '6-7 мин/км' },
  { value: '5-6', label: '5-6 мин/км' },
  { value: '4-5', label: '4-5 мин/км' },
  { value: '4-', label: 'Быстрее 4 мин/км' },
];

export default function PlanWizardModal({ isOpen, onClose, onSubmit, loading = false }: PlanWizardModalProps) {
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState<PlanWizardData>({
    sportType: undefined,
    weeklyDistance: '',
    comfortablePace: '',
    targetDistance: '',
    competitionDate: '',
    hasSpecificGoal: true,
    hasStrengthTraining: false,
    preferredWorkoutDays: [],
  });
  const [maxWeeklyWorkouts, setMaxWeeklyWorkouts] = useState<number | null>(null);
  const [loadingWorkoutCount, setLoadingWorkoutCount] = useState(false);
  const [availableSports, setAvailableSports] = useState<string[]>([]);
  const [competitionTypes, setCompetitionTypes] = useState<CompetitionTypesResponse>({});
  const [loadingCompetitionTypes, setLoadingCompetitionTypes] = useState(false);

  // Определяем, нужен ли шаг выбора вида спорта
  const needsSportSelection = availableSports.length > 1;
  // Добавляем +1 шаг для вопроса о силовых тренировках
  const totalSteps = needsSportSelection ? 7 : 6;

  // Загрузить типы соревнований при открытии модалки
  useEffect(() => {
    if (isOpen && competitionTypes && Object.keys(competitionTypes).length === 0) {
      const loadCompetitionTypes = async () => {
        setLoadingCompetitionTypes(true);
        try {
          const types = await apiClient.getCompetitionTypes();
          setCompetitionTypes(types);

          // Определяем доступные виды спорта
          const sports: string[] = [];
          if (types.running && types.running.length > 0) sports.push('running');
          if (types.cycling && types.cycling.length > 0) sports.push('cycling');
          if (types.swimming && types.swimming.length > 0) sports.push('swimming');
          if (types.triathlon && types.triathlon.length > 0) sports.push('triathlon');

          setAvailableSports(sports);

          // Если только один вид спорта доступен, автоматически выбираем его
          if (sports.length === 1) {
            setFormData(prev => ({ ...prev, sportType: sports[0] }));
          }
        } catch (error) {
          console.error('Ошибка загрузки типов соревнований:', error);
        } finally {
          setLoadingCompetitionTypes(false);
        }
      };

      loadCompetitionTypes();
    }
  }, [isOpen, competitionTypes]);

  const handleNext = async () => {
    if (currentStep < totalSteps) {
      // Определяем, является ли следующий шаг выбором дней
      const nextStepIsWorkoutDays = currentStep === totalSteps - 1;

      // Если переходим на шаг выбора дней, сначала запрашиваем количество тренировок
      if (nextStepIsWorkoutDays && !maxWeeklyWorkouts) {
        setLoadingWorkoutCount(true);
        try {
          const response = await apiClient.getWeeklyWorkoutCount({
            weekly_distance: formData.weeklyDistance,
            comfortable_pace: formData.comfortablePace,
            target_distance: formData.targetDistance,
            competition_date: formData.competitionDate,
            has_specific_goal: formData.hasSpecificGoal,
          });
          setMaxWeeklyWorkouts(response.max_weekly_workouts);
        } catch (error) {
          console.error('Ошибка получения количества тренировок:', error);
          // В случае ошибки используем значение по умолчанию
          setMaxWeeklyWorkouts(6);
        } finally {
          setLoadingWorkoutCount(false);
        }
      }
      setCurrentStep(currentStep + 1);
    }
  };

  const handlePrev = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSubmit = async () => {
    // Если нет конкретной цели, устанавливаем дату через 6 месяцев
    const finalData = { ...formData };
    if (!finalData.hasSpecificGoal) {
      const sixMonthsLater = new Date();
      sixMonthsLater.setMonth(sixMonthsLater.getMonth() + 6);
      finalData.competitionDate = sixMonthsLater.toISOString().split('T')[0];
    }

    await onSubmit(finalData);
  };

  const handleClose = () => {
    setCurrentStep(1);
    setFormData({
      sportType: undefined,
      weeklyDistance: '',
      comfortablePace: '',
      targetDistance: '',
      competitionDate: '',
      hasSpecificGoal: true,
      preferredWorkoutDays: [],
      hasStrengthTraining: false,
    });
    setMaxWeeklyWorkouts(null);
    setAvailableSports([]);
    setCompetitionTypes({});
    onClose();
  };

  // Вспомогательная функция для определения типа текущего шага
  const getCurrentStepType = () => {
    if (needsSportSelection) {
      // С выбором вида спорта: шаги 1-7
      switch (currentStep) {
        case 1: return 'sport-selection';
        case 2: return 'weekly-distance';
        case 3: {
          // Шаг с темпом только для бега и триатлона
          const sportType = formData.sportType;
          if (sportType === 'running' || sportType === 'triathlon') {
            return 'pace';
          } else {
            return 'target-distance';
          }
        }
        case 4: {
          const sportType = formData.sportType;
          if (sportType === 'running' || sportType === 'triathlon') {
            return 'target-distance';
          } else {
            return 'strength-question';
          }
        }
        case 5: {
          const sportType = formData.sportType;
          if (sportType === 'running' || sportType === 'triathlon') {
            return 'strength-question';
          } else {
            return 'competition-date';
          }
        }
        case 6: {
          const sportType = formData.sportType;
          if (sportType === 'running' || sportType === 'triathlon') {
            return 'competition-date';
          } else {
            return 'workout-days';
          }
        }
        case 7: return 'workout-days';
        default: return 'unknown';
      }
    } else {
      // Без выбора вида спорта: шаги 1-6
      const sportType = formData.sportType;
      switch (currentStep) {
        case 1: return 'weekly-distance';
        case 2: {
          if (sportType === 'running' || sportType === 'triathlon') {
            return 'pace';
          } else {
            return 'target-distance';
          }
        }
        case 3: {
          if (sportType === 'running' || sportType === 'triathlon') {
            return 'target-distance';
          } else {
            return 'strength-question';
          }
        }
        case 4: {
          if (sportType === 'running' || sportType === 'triathlon') {
            return 'strength-question';
          } else {
            return 'competition-date';
          }
        }
        case 5: {
          if (sportType === 'running' || sportType === 'triathlon') {
            return 'competition-date';
          } else {
            return 'workout-days';
          }
        }
        case 6: return 'workout-days';
        default: return 'unknown';
      }
    }
  };

  const isStepValid = () => {
    const stepType = getCurrentStepType();

    switch (stepType) {
      case 'sport-selection':
        return !!formData.sportType;
      case 'weekly-distance':
        return formData.weeklyDistance !== '';
      case 'pace':
        return formData.comfortablePace !== '';
      case 'target-distance':
        if (formData.targetDistance === '') return false;
        // Для плавания и велосипеда проверяем, что введено положительное число
        if (formData.sportType === 'swimming' || formData.sportType === 'cycling') {
          const distance = parseFloat(formData.targetDistance);
          return !isNaN(distance) && distance > 0;
        }
        return true;
      case 'strength-question':
        return true; // Всегда валиден, так как это вопрос да/нет
      case 'competition-date':
        return formData.hasSpecificGoal ? formData.competitionDate !== '' : true;
      case 'workout-days':
        const selectedCount = formData.preferredWorkoutDays.length;
        const maxDays = maxWeeklyWorkouts || 7;
        return selectedCount >= 2 && selectedCount <= maxDays;
      default:
        return false;
    }
  };

  const canProceed = isStepValid();

  // Названия дней недели
  const weekDays = [
    { value: 0, label: 'Понедельник' },
    { value: 1, label: 'Вторник' },
    { value: 2, label: 'Среда' },
    { value: 3, label: 'Четверг' },
    { value: 4, label: 'Пятница' },
    { value: 5, label: 'Суббота' },
    { value: 6, label: 'Воскресенье' }
  ];

  const handleDayToggle = (dayValue: number) => {
    setFormData(prev => {
      const currentDays = prev.preferredWorkoutDays;
      const maxDays = maxWeeklyWorkouts || 7;

      if (currentDays.includes(dayValue)) {
        // Убираем день
        return { ...prev, preferredWorkoutDays: currentDays.filter(day => day !== dayValue) };
      } else {
        // Добавляем день, если не превышен лимит
        if (currentDays.length < maxDays) {
          return { ...prev, preferredWorkoutDays: [...currentDays, dayValue].sort() };
        }
        return prev;
      }
    });
  };

  // Вспомогательные функции для получения опций и текстов
  const getWeeklyDistanceOptions = () => {
    const sportType = formData.sportType;
    switch (sportType) {
      case 'swimming':
        return WEEKLY_DISTANCE_OPTIONS_SWIMMING;
      case 'cycling':
        return WEEKLY_DISTANCE_OPTIONS_CYCLING;
      default:
        return WEEKLY_DISTANCE_OPTIONS_RUNNING;
    }
  };

  const getWeeklyDistanceQuestion = () => {
    const sportType = formData.sportType;
    switch (sportType) {
      case 'swimming':
        return 'Сколько Вы в среднем проплываете в неделю?';
      case 'cycling':
        return 'Сколько в среднем Вы проезжаете на велосипеде в неделю?';
      case 'triathlon':
        return 'Сколько Вы в среднем пробегаете в неделю на тренировках?';
      default:
        return 'Сколько Вы в среднем пробегаете в неделю на тренировках?';
    }
  };

  const getTargetDistanceOptions = () => {
    const sportType = formData.sportType;
    if (sportType === 'running') {
      return competitionTypes.running || [];
    } else if (sportType === 'cycling') {
      return competitionTypes.cycling || [];
    } else if (sportType === 'swimming') {
      return competitionTypes.swimming || [];
    } else if (sportType === 'triathlon') {
      return competitionTypes.triathlon || [];
    }
    return [];
  };

  const getTargetDistanceQuestion = () => {
    return 'К какой дистанции Вы хотели бы подготовиться?';
  };

  const getSportTypeLabel = (sportType: string) => {
    switch (sportType) {
      case 'running':
        return 'Бег';
      case 'cycling':
        return 'Велосипед';
      case 'swimming':
        return 'Плавание';
      case 'triathlon':
        return 'Триатлон';
      default:
        return sportType;
    }
  };

  if (!isOpen) return null;

  const currentStepType = getCurrentStepType();

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto">
        <Card className="border-0 shadow-none">
          <CardHeader className="relative pb-2">
            <button
              onClick={handleClose}
              className="absolute right-4 top-4 text-gray-400 hover:text-gray-600 transition-colors"
              disabled={loading}
            >
              <X className="w-5 h-5" />
            </button>
            
            <CardTitle className="text-xl font-bold text-center pr-8">
              Мастер создания планов
            </CardTitle>
            <CardDescription className="text-center">
              Шаг {currentStep} из {totalSteps}
            </CardDescription>
            
            {/* Прогресс-бар */}
            <div className="w-full bg-gray-200 rounded-full h-2 mt-4">
              <div 
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${(currentStep / totalSteps) * 100}%` }}
              />
            </div>
          </CardHeader>

          <CardContent className="pt-4">
            {loadingCompetitionTypes ? (
              <div className="flex flex-col items-center justify-center py-8">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
                <p className="text-gray-600">Загрузка доступных видов спорта...</p>
              </div>
            ) : (
              <>
                {/* Шаг: Выбор вида спорта */}
                {currentStepType === 'sport-selection' && (
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold text-center mb-6">
                      К какому виду спорта Вы готовитесь?
                    </h3>
                    <div className="space-y-3">
                      {availableSports.map((sport) => (
                    <label
                      key={sport}
                      className={`
                        flex items-center p-3 border rounded-lg cursor-pointer transition-all
                        ${formData.sportType === sport
                          ? 'border-blue-500 bg-blue-50 text-blue-700'
                          : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                        }
                      `}
                    >
                      <input
                        type="radio"
                        name="sportType"
                        value={sport}
                        checked={formData.sportType === sport}
                        onChange={(e) => setFormData({ ...formData, sportType: e.target.value, weeklyDistance: '', comfortablePace: '', targetDistance: '' })}
                        className="sr-only"
                      />
                      <div className={`
                        w-4 h-4 rounded-full border-2 mr-3 flex items-center justify-center
                        ${formData.sportType === sport
                          ? 'border-blue-500'
                          : 'border-gray-300'
                        }
                      `}>
                        {formData.sportType === sport && (
                          <div className="w-2 h-2 rounded-full bg-blue-500" />
                        )}
                      </div>
                      <span className="text-sm font-medium">{getSportTypeLabel(sport)}</span>
                    </label>
                  ))}
                </div>
              </div>
            )}

            {/* Шаг: Недельный объем */}
            {currentStepType === 'weekly-distance' && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-center mb-6">
                  {getWeeklyDistanceQuestion()}
                </h3>
                <div className="space-y-3">
                  {getWeeklyDistanceOptions().map((option) => (
                    <label
                      key={option.value}
                      className={`
                        flex items-center p-3 border rounded-lg cursor-pointer transition-all
                        ${formData.weeklyDistance === option.value
                          ? 'border-blue-500 bg-blue-50 text-blue-700'
                          : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                        }
                      `}
                    >
                      <input
                        type="radio"
                        name="weeklyDistance"
                        value={option.value}
                        checked={formData.weeklyDistance === option.value}
                        onChange={(e) => setFormData({ ...formData, weeklyDistance: e.target.value })}
                        className="sr-only"
                      />
                      <div className={`
                        w-4 h-4 rounded-full border-2 mr-3 flex items-center justify-center
                        ${formData.weeklyDistance === option.value
                          ? 'border-blue-500'
                          : 'border-gray-300'
                        }
                      `}>
                        {formData.weeklyDistance === option.value && (
                          <div className="w-2 h-2 rounded-full bg-blue-500" />
                        )}
                      </div>
                      <span className="text-sm font-medium">{option.label}</span>
                    </label>
                  ))}
                </div>
              </div>
            )}

            {/* Шаг: Комфортный темп (только для бега и триатлона) */}
            {currentStepType === 'pace' && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-center mb-6">
                  Какой комфортный темп бега для Вас на длительной тренировке?
                </h3>
                <div className="space-y-3">
                  {PACE_OPTIONS.map((option) => (
                    <label
                      key={option.value}
                      className={`
                        flex items-center p-3 border rounded-lg cursor-pointer transition-all
                        ${formData.comfortablePace === option.value
                          ? 'border-blue-500 bg-blue-50 text-blue-700'
                          : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                        }
                      `}
                    >
                      <input
                        type="radio"
                        name="comfortablePace"
                        value={option.value}
                        checked={formData.comfortablePace === option.value}
                        onChange={(e) => setFormData({ ...formData, comfortablePace: e.target.value })}
                        className="sr-only"
                      />
                      <div className={`
                        w-4 h-4 rounded-full border-2 mr-3 flex items-center justify-center
                        ${formData.comfortablePace === option.value
                          ? 'border-blue-500'
                          : 'border-gray-300'
                        }
                      `}>
                        {formData.comfortablePace === option.value && (
                          <div className="w-2 h-2 rounded-full bg-blue-500" />
                        )}
                      </div>
                      <span className="text-sm font-medium">{option.label}</span>
                    </label>
                  ))}
                </div>
              </div>
            )}

            {/* Шаг: Целевая дистанция */}
            {currentStepType === 'target-distance' && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-center mb-6">
                  {getTargetDistanceQuestion()}
                </h3>

                {/* Для плавания и велосипеда - текстовое поле */}
                {(formData.sportType === 'swimming' || formData.sportType === 'cycling') ? (
                  <div>
                    <label htmlFor="targetDistance" className="block text-sm font-medium text-gray-700 mb-2">
                      {formData.sportType === 'swimming'
                        ? 'Укажите дистанцию в метрах'
                        : 'Укажите дистанцию в километрах'}
                    </label>
                    <Input
                      id="targetDistance"
                      type="number"
                      min="1"
                      placeholder={formData.sportType === 'swimming' ? 'Например: 1500' : 'Например: 40'}
                      value={formData.targetDistance}
                      onChange={(e) => setFormData({ ...formData, targetDistance: e.target.value })}
                      className="w-full"
                    />
                  </div>
                ) : (
                  /* Для бега и триатлона - выбор из списка */
                  <div className="space-y-3">
                    {getTargetDistanceOptions().map((option) => (
                      <label
                        key={option.value}
                        className={`
                          flex items-center p-3 border rounded-lg cursor-pointer transition-all
                          ${formData.targetDistance === option.value
                            ? 'border-blue-500 bg-blue-50 text-blue-700'
                            : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                          }
                        `}
                      >
                        <input
                          type="radio"
                          name="targetDistance"
                          value={option.value}
                          checked={formData.targetDistance === option.value}
                          onChange={(e) => setFormData({ ...formData, targetDistance: e.target.value })}
                          className="sr-only"
                        />
                        <div className={`
                          w-4 h-4 rounded-full border-2 mr-3 flex items-center justify-center
                          ${formData.targetDistance === option.value
                            ? 'border-blue-500'
                            : 'border-gray-300'
                          }
                        `}>
                          {formData.targetDistance === option.value && (
                            <div className="w-2 h-2 rounded-full bg-blue-500" />
                          )}
                        </div>
                        <span className="text-sm font-medium">{option.label}</span>
                      </label>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Шаг: Вопрос о силовых тренировках */}
            {currentStepType === 'strength-question' && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-center mb-6">
                  Есть ли возможность заниматься силовыми тренировками в зале?
                </h3>
                <div className="space-y-3">
                  <label
                    className={`
                      flex items-center p-3 border rounded-lg cursor-pointer transition-all
                      ${formData.hasStrengthTraining === true
                        ? 'border-blue-500 bg-blue-50 text-blue-700'
                        : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                      }
                    `}
                  >
                    <input
                      type="radio"
                      name="hasStrengthTraining"
                      value="true"
                      checked={formData.hasStrengthTraining === true}
                      onChange={() => setFormData({ ...formData, hasStrengthTraining: true })}
                      className="sr-only"
                    />
                    <div className={`
                      w-4 h-4 rounded-full border-2 mr-3 flex items-center justify-center
                      ${formData.hasStrengthTraining === true
                        ? 'border-blue-500'
                        : 'border-gray-300'
                      }
                    `}>
                      {formData.hasStrengthTraining === true && (
                        <div className="w-2 h-2 rounded-full bg-blue-500" />
                      )}
                    </div>
                    <span className="text-sm font-medium">Да</span>
                  </label>

                  <label
                    className={`
                      flex items-center p-3 border rounded-lg cursor-pointer transition-all
                      ${formData.hasStrengthTraining === false
                        ? 'border-blue-500 bg-blue-50 text-blue-700'
                        : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                      }
                    `}
                  >
                    <input
                      type="radio"
                      name="hasStrengthTraining"
                      value="false"
                      checked={formData.hasStrengthTraining === false}
                      onChange={() => setFormData({ ...formData, hasStrengthTraining: false })}
                      className="sr-only"
                    />
                    <div className={`
                      w-4 h-4 rounded-full border-2 mr-3 flex items-center justify-center
                      ${formData.hasStrengthTraining === false
                        ? 'border-blue-500'
                        : 'border-gray-300'
                      }
                    `}>
                      {formData.hasStrengthTraining === false && (
                        <div className="w-2 h-2 rounded-full bg-blue-500" />
                      )}
                    </div>
                    <span className="text-sm font-medium">Нет</span>
                  </label>
                </div>
              </div>
            )}

            {/* Шаг: Дата соревнования */}
            {currentStepType === 'competition-date' && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-center mb-6">
                  Какая дата ключевого соревнования?
                </h3>
                
                <div className="space-y-4">
                  <label className="flex items-center space-x-3">
                    <input
                      type="checkbox"
                      checked={!formData.hasSpecificGoal}
                      onChange={(e) => setFormData({ 
                        ...formData, 
                        hasSpecificGoal: !e.target.checked,
                        competitionDate: e.target.checked ? '' : formData.competitionDate
                      })}
                      className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 focus:ring-2"
                    />
                    <span className="text-sm font-medium text-gray-700">
                      Нет конкретной цели
                    </span>
                  </label>
                  
                  {formData.hasSpecificGoal && (
                    <div>
                      <label htmlFor="competitionDate" className="block text-sm font-medium text-gray-700 mb-2">
                        Дата соревнования
                      </label>
                      <Input
                        id="competitionDate"
                        type="date"
                        value={formData.competitionDate}
                        onChange={(e) => setFormData({ ...formData, competitionDate: e.target.value })}
                        min={new Date().toISOString().split('T')[0]}
                        className="w-full"
                      />
                    </div>
                  )}
                  
                  {!formData.hasSpecificGoal && (
                    <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                      <p className="text-sm text-blue-700">
                        План будет создан на 6 месяцев вперед для общего развития физической формы.
                      </p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Шаг: Предпочтительные дни для тренировок */}
            {currentStepType === 'workout-days' && (
              <div className="space-y-4">
                {loadingWorkoutCount ? (
                  <div className="flex flex-col items-center justify-center py-8">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
                    <p className="text-gray-600">Рассчитываем количество тренировок...</p>
                  </div>
                ) : (
                  <>
                    <h3 className="text-lg font-semibold text-center mb-2">
                      В какие дни недели Вам удобнее тренироваться?
                    </h3>
                    
                    {maxWeeklyWorkouts && (
                      <div className="p-3 bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-lg mb-4">
                        <p className="text-sm font-semibold text-blue-900 text-center">
                          В вашем плане будет максимум {maxWeeklyWorkouts} {maxWeeklyWorkouts === 1 ? 'тренировка' : maxWeeklyWorkouts <= 4 ? 'тренировки' : 'тренировок'} в неделю
                        </p>
                        <p className="text-xs text-blue-700 text-center mt-1">
                          {maxWeeklyWorkouts < 7 
                            ? `Выберите от 2 до ${maxWeeklyWorkouts} дней для тренировок`
                            : 'Выберите минимум 2 дня для тренировок'
                          }
                        </p>
                      </div>
                    )}
                    
                    <div className="space-y-2">
                      {weekDays.map((day) => {
                        const isSelected = formData.preferredWorkoutDays.includes(day.value);
                        const maxDays = maxWeeklyWorkouts || 7;
                        const isDisabled = !isSelected && formData.preferredWorkoutDays.length >= maxDays;
                        
                        return (
                          <label
                            key={day.value}
                            className={`
                              flex items-center p-3 border rounded-lg transition-all
                              ${isSelected
                                ? 'border-blue-500 bg-blue-50 text-blue-700'
                                : isDisabled
                                ? 'border-gray-200 bg-gray-50 text-gray-400 cursor-not-allowed'
                                : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50 cursor-pointer'
                              }
                            `}
                          >
                            <input
                              type="checkbox"
                              checked={isSelected}
                              onChange={() => handleDayToggle(day.value)}
                              disabled={isDisabled}
                              className="sr-only"
                            />
                            <div className={`
                              w-4 h-4 rounded border-2 mr-3 flex items-center justify-center
                              ${isSelected
                                ? 'border-blue-500 bg-blue-500'
                                : isDisabled
                                ? 'border-gray-300 bg-gray-100'
                                : 'border-gray-300'
                              }
                            `}>
                              {isSelected && (
                                <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                                </svg>
                              )}
                            </div>
                            <span className="text-sm font-medium">{day.label}</span>
                          </label>
                        );
                      })}
                    </div>
                    
                    <div className={`p-3 border rounded-lg ${
                      formData.preferredWorkoutDays.length >= 2 && formData.preferredWorkoutDays.length <= (maxWeeklyWorkouts || 7)
                        ? 'bg-green-50 border-green-200'
                        : formData.preferredWorkoutDays.length < 2
                        ? 'bg-orange-50 border-orange-200'
                        : 'bg-red-50 border-red-200'
                    }`}>
                      <p className={`text-sm font-medium ${
                        formData.preferredWorkoutDays.length >= 2 && formData.preferredWorkoutDays.length <= (maxWeeklyWorkouts || 7)
                          ? 'text-green-700'
                          : formData.preferredWorkoutDays.length < 2
                          ? 'text-orange-700'
                          : 'text-red-700'
                      }`}>
                        {formData.preferredWorkoutDays.length < 2 
                          ? `Выбрано дней: ${formData.preferredWorkoutDays.length}. Выберите минимум 2 дня.`
                          : formData.preferredWorkoutDays.length > (maxWeeklyWorkouts || 7)
                          ? `Выбрано слишком много дней (${formData.preferredWorkoutDays.length}). Максимум: ${maxWeeklyWorkouts || 7}.`
                          : `✓ Выбрано дней: ${formData.preferredWorkoutDays.length} из ${maxWeeklyWorkouts || 7}`
                        }
                      </p>
                    </div>
                  </>
                )}
              </div>
            )}
            </>
            )}

            {/* Кнопки навигации */}
            <div className="flex justify-between mt-8 pt-4 border-t">
              <Button
                variant="outline"
                onClick={handlePrev}
                disabled={currentStep === 1 || loading}
                className="flex items-center"
              >
                <ChevronLeft className="w-4 h-4 mr-1" />
                Назад
              </Button>

              {currentStep < totalSteps ? (
                <Button
                  onClick={handleNext}
                  disabled={!canProceed || loading || loadingWorkoutCount}
                  className="flex items-center"
                >
                  {loadingWorkoutCount ? 'Загрузка...' : 'Далее'}
                  {!loadingWorkoutCount && <ChevronRight className="w-4 h-4 ml-1" />}
                </Button>
              ) : (
                <Button
                  onClick={handleSubmit}
                  disabled={!canProceed || loading}
                  className="flex items-center"
                >
                  {loading ? 'Создание плана...' : 'Создать план'}
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
