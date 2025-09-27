'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { X, ChevronLeft, ChevronRight } from 'lucide-react';

export interface PlanWizardData {
  weeklyDistance: string;
  comfortablePace: string;
  targetDistance: string;
  competitionDate: string;
  hasSpecificGoal: boolean;
}

interface PlanWizardModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: PlanWizardData) => Promise<void>;
  loading?: boolean;
}

const WEEKLY_DISTANCE_OPTIONS = [
  { value: 'beginner', label: 'Только начинаю бегать' },
  { value: '5-10', label: '5-10 км' },
  { value: '10-30', label: '10-30 км' },
  { value: '30-50', label: '30-50 км' },
  { value: '50+', label: 'Больше 50 км' },
];

const PACE_OPTIONS = [
  { value: '8+', label: 'Медленнее 8 мин/км' },
  { value: '7-8', label: '7-8 мин/км' },
  { value: '6-7', label: '6-7 мин/км' },
  { value: '5-6', label: '5-6 мин/км' },
  { value: '4-5', label: '4-5 мин/км' },
  { value: '4-', label: 'Быстрее 4 мин/км' },
];

const TARGET_DISTANCE_OPTIONS = [
  { value: '5k', label: '5 км' },
  { value: '10k', label: '10 км' },
  { value: '21k', label: '21 км (полумарафон)' },
  { value: '42k', label: '42 км (марафон)' },
];

export default function PlanWizardModal({ isOpen, onClose, onSubmit, loading = false }: PlanWizardModalProps) {
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState<PlanWizardData>({
    weeklyDistance: '',
    comfortablePace: '',
    targetDistance: '',
    competitionDate: '',
    hasSpecificGoal: true,
  });

  const totalSteps = 4;

  const handleNext = () => {
    if (currentStep < totalSteps) {
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
      weeklyDistance: '',
      comfortablePace: '',
      targetDistance: '',
      competitionDate: '',
      hasSpecificGoal: true,
    });
    onClose();
  };

  const isStepValid = () => {
    switch (currentStep) {
      case 1:
        return formData.weeklyDistance !== '';
      case 2:
        return formData.comfortablePace !== '';
      case 3:
        return formData.targetDistance !== '';
      case 4:
        return formData.hasSpecificGoal ? formData.competitionDate !== '' : true;
      default:
        return false;
    }
  };

  const canProceed = isStepValid();

  if (!isOpen) return null;

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
            {/* Шаг 1: Недельный километраж */}
            {currentStep === 1 && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-center mb-6">
                  Сколько Вы в среднем пробегаете в неделю на тренировках?
                </h3>
                <div className="space-y-3">
                  {WEEKLY_DISTANCE_OPTIONS.map((option) => (
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

            {/* Шаг 2: Комфортный темп */}
            {currentStep === 2 && (
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

            {/* Шаг 3: Целевая дистанция */}
            {currentStep === 3 && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-center mb-6">
                  К какой дистанции Вы хотели бы подготовиться по бегу?
                </h3>
                <div className="space-y-3">
                  {TARGET_DISTANCE_OPTIONS.map((option) => (
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
              </div>
            )}

            {/* Шаг 4: Дата соревнования */}
            {currentStep === 4 && (
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
                  disabled={!canProceed || loading}
                  className="flex items-center"
                >
                  Далее
                  <ChevronRight className="w-4 h-4 ml-1" />
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
