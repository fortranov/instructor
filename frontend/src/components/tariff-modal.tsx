'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import apiClient from '@/lib/api';
import { TariffPriceResponse } from '@/types/api';
import { getErrorMessage } from '@/lib/utils';
import { X, Check, Star } from 'lucide-react';

interface TariffModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentTariff: string | null;
  onSuccess: () => void;
}

export default function TariffModal({ isOpen, onClose, currentTariff, onSuccess }: TariffModalProps) {
  const [selectedMonths, setSelectedMonths] = useState(1);
  const [priceInfo, setPriceInfo] = useState<TariffPriceResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [purchasing, setPurchasing] = useState(false);
  const [error, setError] = useState('');

  const monthOptions = [
    { value: 1, label: '1 месяц' },
    { value: 2, label: '2 месяца', discount: 5 },
    { value: 6, label: '6 месяцев', discount: 10 },
    { value: 12, label: '12 месяцев', discount: 15 }
  ];

  useEffect(() => {
    if (isOpen) {
      fetchPriceInfo(selectedMonths);
    }
  }, [isOpen, selectedMonths]);

  const fetchPriceInfo = async (months: number) => {
    setLoading(true);
    setError('');
    
    try {
      const price = await apiClient.getTariffPrice(months);
      setPriceInfo(price);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const handlePurchase = async () => {
    if (!priceInfo) return;
    
    setPurchasing(true);
    setError('');
    
    try {
      const result = await apiClient.purchaseTariff({
        tariff_type: 'pro',
        months: selectedMonths
      });
      
      alert(`${result.message}\nЦена: ${result.price} руб.\nЭкономия: ${result.savings} руб.\n\n${result.note}`);
      onSuccess();
      onClose();
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setPurchasing(false);
    }
  };

  if (!isOpen) return null;

  const isPro = currentTariff === 'pro';

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-md w-full max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center p-6 border-b">
          <h2 className="text-xl font-semibold text-gray-900">
            {isPro ? 'Продлить тариф Про' : 'Купить тариф Про'}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="p-6">
          {error && (
            <div className="mb-4 bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-md">
              {error}
            </div>
          )}

          {!isPro && (
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">
                Преимущества тарифа Про
              </h3>
              <ul className="space-y-2">
                <li className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-green-600" />
                  <span className="text-sm text-gray-700">Просмотр полного плана тренировок</span>
                </li>
                <li className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-green-600" />
                  <span className="text-sm text-gray-700">Доступ ко всем функциям</span>
                </li>
                <li className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-green-600" />
                  <span className="text-sm text-gray-700">Приоритетная поддержка</span>
                </li>
              </ul>
            </div>
          )}

          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">
              Выберите период {isPro ? 'продления' : 'подписки'}
            </h3>
            <div className="grid grid-cols-1 gap-3">
              {monthOptions.map((option) => (
                <Card
                  key={option.value}
                  className={`cursor-pointer transition-all ${
                    selectedMonths === option.value
                      ? 'ring-2 ring-blue-500 bg-blue-50'
                      : 'hover:bg-gray-50'
                  }`}
                  onClick={() => setSelectedMonths(option.value)}
                >
                  <CardContent className="p-4">
                    <div className="flex justify-between items-center">
                      <div className="flex items-center gap-2">
                        <div className={`w-4 h-4 rounded-full border-2 ${
                          selectedMonths === option.value
                            ? 'bg-blue-500 border-blue-500'
                            : 'border-gray-300'
                        }`}>
                          {selectedMonths === option.value && (
                            <div className="w-2 h-2 bg-white rounded-full m-0.5" />
                          )}
                        </div>
                        <span className="font-medium">{option.label}</span>
                        {option.discount && (
                          <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">
                            -{option.discount}%
                          </span>
                        )}
                      </div>
                      {priceInfo && selectedMonths === option.value && (
                        <div className="text-right">
                          <div className="font-semibold text-gray-900">
                            {priceInfo.final_price.toFixed(0)} ₽
                          </div>
                          {priceInfo.total_savings > 0 && (
                            <div className="text-sm text-green-600">
                              Экономия: {priceInfo.total_savings.toFixed(0)} ₽
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {priceInfo && (
            <Card className="mb-6 bg-gray-50">
              <CardContent className="p-4">
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Базовая цена за месяц:</span>
                    <span className="text-sm">{priceInfo.base_price.toFixed(0)} ₽</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Количество месяцев:</span>
                    <span className="text-sm">{priceInfo.months}</span>
                  </div>
                  {priceInfo.discount_percent > 0 && (
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Скидка:</span>
                      <span className="text-sm text-green-600">-{priceInfo.discount_percent}%</span>
                    </div>
                  )}
                  <hr className="my-2" />
                  <div className="flex justify-between font-semibold">
                    <span>Итого к оплате:</span>
                    <span>{priceInfo.final_price.toFixed(0)} ₽</span>
                  </div>
                  {priceInfo.total_savings > 0 && (
                    <div className="text-sm text-green-600 text-center">
                      Вы экономите {priceInfo.total_savings.toFixed(0)} ₽!
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          )}

          <div className="flex gap-3">
            <Button
              variant="outline"
              onClick={onClose}
              className="flex-1"
              disabled={purchasing}
            >
              Отмена
            </Button>
            <Button
              onClick={handlePurchase}
              className="flex-1 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
              disabled={loading || purchasing || !priceInfo}
            >
              {purchasing ? (
                'Обработка...'
              ) : (
                <>
                  <Star className="w-4 h-4 mr-2" />
                  {isPro ? 'Продлить' : 'Купить'} за {priceInfo?.final_price.toFixed(0)} ₽
                </>
              )}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
