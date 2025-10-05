'use client';

import { useEffect, useState } from 'react';
import { Save, Check, X } from 'lucide-react';
import apiClient from '@/lib/api';

interface Tariff {
  id: number;
  name: string;
  type: string;
  view_full_plan: boolean;
  view_two_weeks: boolean;
  created_at: string;
  updated_at: string;
}

interface TariffSettings {
  test: {
    view_full_plan: boolean;
    view_two_weeks: boolean;
  };
  trial: {
    view_full_plan: boolean;
    view_two_weeks: boolean;
  };
  pro: {
    view_full_plan: boolean;
    view_two_weeks: boolean;
  };
}

export default function TariffsPage() {
  const [tariffs, setTariffs] = useState<Tariff[]>([]);
  const [settings, setSettings] = useState<TariffSettings>({
    test: { view_full_plan: false, view_two_weeks: true },
    trial: { view_full_plan: false, view_two_weeks: true },
    pro: { view_full_plan: true, view_two_weeks: true }
  });
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState<string | null>(null);
  const [proTariffPrice, setProTariffPrice] = useState('999.00');
  const [priceLoading, setPriceLoading] = useState(false);

  useEffect(() => {
    fetchTariffs();
    fetchProTariffPrice();
  }, []);

  const fetchProTariffPrice = async () => {
    setPriceLoading(true);
    try {
      const setting = await apiClient.getAppSetting('pro_tariff_price');
      setProTariffPrice(setting.value);
    } catch (error) {
      console.error('Ошибка загрузки цены тарифа:', error);
      // Если настройка не найдена, инициализируем значения по умолчанию
      try {
        await apiClient.initDefaultSettings();
        setProTariffPrice('999.00');
      } catch (initError) {
        console.error('Ошибка инициализации настроек:', initError);
      }
    } finally {
      setPriceLoading(false);
    }
  };

  const fetchTariffs = async () => {
    try {
      const data = await apiClient.getAdminTariffs();
      setTariffs(data);
        
      // Обновляем настройки на основе полученных данных
      const newSettings: TariffSettings = {
        test: { view_full_plan: false, view_two_weeks: true },
        trial: { view_full_plan: false, view_two_weeks: true },
        pro: { view_full_plan: true, view_two_weeks: true }
      };

      data.forEach((tariff: Tariff) => {
        if (tariff.type in newSettings) {
          newSettings[tariff.type as keyof TariffSettings] = {
            view_full_plan: tariff.view_full_plan,
            view_two_weeks: tariff.view_two_weeks
          };
        }
      });

      setSettings(newSettings);
    } catch (error) {
      console.error('Ошибка загрузки тарифов:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSettingChange = (tariffType: keyof TariffSettings, setting: string, value: boolean) => {
    setSettings(prev => ({
      ...prev,
      [tariffType]: {
        ...prev[tariffType],
        [setting]: value
      }
    }));
  };

  const handleSave = async () => {
    setIsSaving(true);
    setSaveMessage(null);

    try {
      // Сохраняем настройки тарифов
      await apiClient.updateTariffs(settings);
      
      // Сохраняем цену тарифа Про
      await apiClient.updateAppSetting('pro_tariff_price', {
        key: 'pro_tariff_price',
        value: proTariffPrice,
        description: 'Цена тарифа Про за месяц (в рублях)'
      });
      
      setSaveMessage('Настройки тарифов и цена успешно сохранены');
      await fetchTariffs(); // Обновляем данные
    } catch (error) {
      console.error('Ошибка сохранения настроек:', error);
      setSaveMessage('Ошибка сохранения настроек');
    } finally {
      setIsSaving(false);
      // Убираем сообщение через 3 секунды
      setTimeout(() => setSaveMessage(null), 3000);
    }
  };

  const tariffNames: Record<string, string> = {
    test: 'Тестовый',
    trial: 'Пробный',
    pro: 'Про'
  };

  const settingsLabels = {
    view_full_plan: 'Просмотр всего плана',
    view_two_weeks: 'Просмотр двух недель'
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Тарифы</h1>
        <p className="mt-2 text-gray-600">
          Настройка функционала тарифных планов
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

      {/* Price settings */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Настройка цены</h3>
        <div className="max-w-md">
          <label htmlFor="proTariffPrice" className="block text-sm font-medium text-gray-700 mb-2">
            Цена тарифа Про за месяц (в рублях)
          </label>
          <div className="relative">
            <input
              type="number"
              id="proTariffPrice"
              value={proTariffPrice}
              onChange={(e) => setProTariffPrice(e.target.value)}
              disabled={priceLoading}
              className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
              placeholder="999.00"
              step="0.01"
              min="0"
            />
            {priceLoading && (
              <div className="absolute right-3 top-2">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
              </div>
            )}
          </div>
          <p className="mt-2 text-sm text-gray-500">
            Эта цена будет использоваться для расчета стоимости подписки с учетом скидок за длительность.
          </p>
        </div>
      </div>

      {/* Tariffs settings table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Настройки
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Тестовый
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Пробный
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Про
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {Object.entries(settingsLabels).map(([settingKey, settingLabel]) => (
                <tr key={settingKey} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {settingLabel}
                  </td>
                  {Object.entries(tariffNames).map(([tariffType]) => (
                    <td key={tariffType} className="px-6 py-4 whitespace-nowrap text-center">
                      <label className="inline-flex items-center">
                        <input
                          type="checkbox"
                          checked={settings[tariffType as keyof TariffSettings][settingKey as keyof typeof settings.test]}
                          onChange={(e) => handleSettingChange(
                            tariffType as keyof TariffSettings,
                            settingKey,
                            e.target.checked
                          )}
                          className="form-checkbox h-5 w-5 text-blue-600 rounded focus:ring-blue-500 focus:ring-2"
                        />
                      </label>
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Description */}
      <div className="bg-blue-50 rounded-lg p-6">
        <h3 className="text-lg font-medium text-blue-900 mb-3">Описание настроек</h3>
        <div className="space-y-2 text-sm text-blue-800">
          <p>
            <strong>Просмотр всего плана:</strong> Пользователи с этой настройкой могут видеть все свои тренировки в плане без ограничений по времени.
          </p>
          <p>
            <strong>Просмотр двух недель:</strong> Пользователи с этой настройкой могут видеть только тренировки на следующие две недели.
          </p>
        </div>
      </div>

      {/* Save button */}
      <div className="flex justify-end">
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
          {isSaving ? 'Сохранение...' : 'Сохранить настройки'}
        </button>
      </div>

      {/* Current tariffs info */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Информация о тарифах</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {tariffs.map((tariff) => (
            <div key={tariff.id} className="border border-gray-200 rounded-lg p-4">
              <h4 className="font-medium text-gray-900 mb-2">{tariff.name}</h4>
              <div className="space-y-1 text-sm text-gray-600">
                <div className="flex items-center justify-between">
                  <span>Просмотр всего плана:</span>
                  <span className={tariff.view_full_plan ? 'text-green-600' : 'text-red-600'}>
                    {tariff.view_full_plan ? 'Да' : 'Нет'}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span>Просмотр двух недель:</span>
                  <span className={tariff.view_two_weeks ? 'text-green-600' : 'text-red-600'}>
                    {tariff.view_two_weeks ? 'Да' : 'Нет'}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
