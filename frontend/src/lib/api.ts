import axios, { AxiosResponse } from 'axios';
import {
  User,
  UserRegistration,
  UserLogin,
  Token,
  UserUpdate,
  TrainingPlan,
  TrainingPlanCreate,
  WorkoutsByDateResponse,
  CompetitionTypesResponse,
  SportTypeOption,
  WorkoutTypeOption,
  WorkoutDateUpdate,
  WorkoutCompletionMarkCreate,
  WorkoutCompletionMarkResponse,
  PlanWizardRequest,
  PlanWizardResponse,
  WeeklyWorkoutCountRequest,
  WeeklyWorkoutCountResponse,
  AdminUser,
  UserTariffUpdate,
  Tariff,
  TariffsUpdateRequest,
  WorkoutCoefficients,
  WorkoutCoefficientsUpdate
} from '@/types/api';

// Используем относительный путь - Next.js проксирует запросы к бэкенду
const API_BASE_URL = '/api/v1';

class ApiClient {
  private baseURL: string;
  private token: string | null = null;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
    
    // Загрузить токен из localStorage при инициализации
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('token');
    }
  }

  private getHeaders() {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    return headers;
  }

  private async request<T>(
    method: 'GET' | 'POST' | 'PUT' | 'DELETE',
    endpoint: string,
    data?: unknown
  ): Promise<T> {
    try {
      const response: AxiosResponse<T> = await axios({
        method,
        url: `${this.baseURL}${endpoint}`,
        data,
        headers: this.getHeaders(),
      });

      return response.data;
    } catch (error: unknown) {
      if (error && typeof error === 'object' && 'response' in error) {
        const axiosError = error as { response?: { data?: { detail?: string } } };
        if (axiosError.response?.data?.detail) {
          throw new Error(axiosError.response.data.detail);
        }
      }
      if (error instanceof Error) {
        throw new Error(error.message);
      }
      throw new Error('Произошла ошибка при запросе к серверу');
    }
  }

  // Методы аутентификации
  async register(userData: UserRegistration): Promise<User> {
    return this.request<User>('POST', '/auth/register', userData);
  }

  async login(userData: UserLogin): Promise<Token> {
    const tokenData = await this.request<Token>('POST', '/auth/login', userData);
    this.setToken(tokenData.access_token);
    return tokenData;
  }

  async getCurrentUser(): Promise<User> {
    return this.request<User>('GET', '/auth/me');
  }

  async updateCurrentUser(userData: UserUpdate): Promise<User> {
    return this.request<User>('PUT', '/auth/me', userData);
  }

  // Методы работы с планами тренировок
  async createTrainingPlan(planData: TrainingPlanCreate): Promise<TrainingPlan> {
    return this.request<TrainingPlan>('POST', '/plans/create', planData);
  }

  async getTrainingPlan(uin: string): Promise<TrainingPlan> {
    return this.request<TrainingPlan>('GET', `/plans/${uin}`);
  }

  async getWorkoutsByDateRange(
    uin: string,
    startDate: string,
    endDate: string
  ): Promise<WorkoutsByDateResponse> {
    return this.request<WorkoutsByDateResponse>(
      'GET',
      `/plans/${uin}/workouts?start_date=${startDate}&end_date=${endDate}`
    );
  }

  async deleteTrainingPlan(uin: string): Promise<void> {
    return this.request<void>('DELETE', `/plans/${uin}`);
  }

  async updateWorkoutDate(uin: string, workoutUpdate: WorkoutDateUpdate): Promise<{ message: string }> {
    return this.request<{ message: string }>('PUT', `/plans/${uin}/workouts/update-date`, workoutUpdate);
  }

  // Методы получения справочных данных
  async getCompetitionTypes(): Promise<CompetitionTypesResponse> {
    return this.request<CompetitionTypesResponse>('GET', '/competition-types');
  }

  async getSportTypes(): Promise<SportTypeOption[]> {
    return this.request<SportTypeOption[]>('GET', '/sport-types');
  }

  async getWorkoutTypes(): Promise<WorkoutTypeOption[]> {
    return this.request<WorkoutTypeOption[]>('GET', '/workout-types');
  }

  // Методы управления токеном
  setToken(token: string) {
    this.token = token;
    if (typeof window !== 'undefined') {
      localStorage.setItem('token', token);
    }
  }

  removeToken() {
    this.token = null;
    if (typeof window !== 'undefined') {
      localStorage.removeItem('token');
    }
  }

  getToken(): string | null {
    return this.token;
  }

  isAuthenticated(): boolean {
    return !!this.token;
  }

  // Методы для отметок выполнения тренировок
  async markWorkoutCompleted(workoutId: number, completionData: WorkoutCompletionMarkCreate): Promise<WorkoutCompletionMarkResponse> {
    return this.request<WorkoutCompletionMarkResponse>('POST', `/workouts/${workoutId}/completion`, completionData);
  }

  // Мастер создания планов
  async createPlanWithWizard(wizardData: PlanWizardRequest): Promise<PlanWizardResponse> {
    return this.request<PlanWizardResponse>('POST', '/plans/wizard', wizardData);
  }

  async getWeeklyWorkoutCount(countData: WeeklyWorkoutCountRequest): Promise<WeeklyWorkoutCountResponse> {
    return this.request<WeeklyWorkoutCountResponse>('POST', '/plans/wizard/workout-count', countData);
  }

  async unmarkWorkoutCompleted(workoutId: number): Promise<void> {
    return this.request<void>('DELETE', `/workouts/${workoutId}/completion`);
  }

  async getWorkoutCompletion(workoutId: number): Promise<WorkoutCompletionMarkResponse> {
    return this.request<WorkoutCompletionMarkResponse>('GET', `/workouts/${workoutId}/completion`);
  }

  // Методы для статистики
  async getYearlyStatistics(year: number): Promise<{
    year: number;
    total_planned_duration: number;
    total_completed_duration: number;
    total_planned_workouts: number;
    total_completed_workouts: number;
    weekly_stats: Array<{
      week_start: string;
      week_end: string;
      planned_duration: number;
      completed_duration: number;
      planned_workouts: number;
      completed_workouts: number;
    }>;
  }> {
    return this.request<{
      year: number;
      total_planned_duration: number;
      total_completed_duration: number;
      total_planned_workouts: number;
      total_completed_workouts: number;
      weekly_stats: Array<{
        week_start: string;
        week_end: string;
        planned_duration: number;
        completed_duration: number;
        planned_workouts: number;
        completed_workouts: number;
      }>;
    }>('GET', `/statistics/yearly/${year}`);
  }

  async getAvailableYears(): Promise<{ years: number[] }> {
    return this.request<{ years: number[] }>('GET', '/statistics/available-years');
  }

  // Проверка здоровья сервиса
  async healthCheck(): Promise<{ status: string; message: string }> {
    return this.request<{ status: string; message: string }>('GET', '/health');
  }

  // Админские методы
  
  // Проверка прав администратора
  async checkAdminRights(): Promise<{ is_admin: boolean; user_email: string; message: string }> {
    return this.request<{ is_admin: boolean; user_email: string; message: string }>('GET', '/admin/check-admin');
  }

  // Управление пользователями
  async getAdminUsers(): Promise<AdminUser[]> {
    console.log('API: Запрос списка пользователей...');
    try {
      const result = await this.request<AdminUser[]>('GET', '/admin/users');
      console.log('API: Получен список пользователей:', result);
      return result;
    } catch (error) {
      console.error('API: Ошибка получения списка пользователей:', error);
      throw error;
    }
  }

  async updateUserTariff(userTariffUpdate: UserTariffUpdate): Promise<{ message: string }> {
    console.log('API: Обновление тарифа пользователя:', userTariffUpdate);
    try {
      const result = await this.request<{ message: string }>('PUT', '/admin/users/tariff', userTariffUpdate);
      console.log('API: Тариф пользователя обновлен:', result);
      return result;
    } catch (error) {
      console.error('API: Ошибка обновления тарифа пользователя:', error);
      throw error;
    }
  }

  // Управление тарифами
  async getAdminTariffs(): Promise<Tariff[]> {
    return this.request<Tariff[]>('GET', '/admin/tariffs');
  }

  async updateTariffs(tariffsUpdate: TariffsUpdateRequest): Promise<{ message: string }> {
    return this.request<{ message: string }>('PUT', '/admin/tariffs', tariffsUpdate);
  }

  // Управление коэффициентами тренировок
  async getWorkoutCoefficients(): Promise<WorkoutCoefficients> {
    console.log('API: Запрос коэффициентов тренировок...');
    try {
      const result = await this.request<WorkoutCoefficients>('GET', '/admin/workout-coefficients');
      console.log('API: Получены коэффициенты тренировок:', result);
      return result;
    } catch (error) {
      console.error('API: Ошибка получения коэффициентов тренировок:', error);
      throw error;
    }
  }

  async updateWorkoutCoefficients(coefficientsUpdate: WorkoutCoefficientsUpdate): Promise<{ message: string }> {
    return this.request<{ message: string }>('PUT', '/admin/workout-coefficients', coefficientsUpdate);
  }
}

// Создаем единственный экземпляр API клиента
const apiClient = new ApiClient();

export default apiClient;
