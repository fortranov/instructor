export interface User {
  id: number;
  uin: string;
  email: string;
  first_name?: string;
  last_name?: string;
  is_active: boolean;
  preferred_workout_days?: number[];
  created_at: string;
}

export interface UserRegistration {
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
}

export interface UserLogin {
  email: string;
  password: string;
}

export interface Token {
  access_token: string;
  token_type: string;
  user: User;
}

export interface UserUpdate {
  first_name?: string;
  last_name?: string;
  email?: string;
  current_password?: string;
  new_password?: string;
  preferred_workout_days?: number[];
}

export interface TrainingPlanCreate {
  uin: string;
  complexity: number;
  competition_date: string;
  competition_type: CompetitionType;
  competition_distance?: number;
}

export interface Workout {
  id: number;
  date: string;
  sport_type: SportType;
  duration_minutes: number;
  workout_type: WorkoutType;
  is_completed?: boolean;
}

export interface TrainingPlan {
  id: number;
  complexity: number;
  competition_date: string;
  competition_type: CompetitionType;
  competition_distance?: number;
  created_at: string;
  updated_at: string;
  workouts: Workout[];
}

export interface WorkoutsByDateResponse {
  uin: string;
  workouts: Workout[];
}

export enum SportType {
  RUNNING = "running",
  CYCLING = "cycling",
  SWIMMING = "swimming"
}

export enum WorkoutType {
  ENDURANCE = "endurance",
  INTERVAL = "interval", 
  RECOVERY = "recovery"
}

export enum CompetitionType {
  RUN_10K = "run_10k",
  RUN_HALF_MARATHON = "run_half_marathon",
  RUN_MARATHON = "run_marathon",
  CYCLING = "cycling",
  SWIMMING = "swimming",
  TRIATHLON_SPRINT = "triathlon_sprint",
  TRIATHLON_OLYMPIC = "triathlon_olympic",
  TRIATHLON_IRONMAN = "triathlon_ironman"
}

export interface CompetitionTypeOption {
  value: CompetitionType;
  label: string;
}

export interface SportTypeOption {
  value: SportType;
  label: string;
}

export interface WorkoutTypeOption {
  value: WorkoutType;
  label: string;
}

export interface CompetitionTypesResponse {
  running: CompetitionTypeOption[];
  cycling: CompetitionTypeOption[];
  swimming: CompetitionTypeOption[];
  triathlon: CompetitionTypeOption[];
}

export interface ApiError {
  detail: string;
}

export interface WorkoutDateUpdate {
  workout_id: number;
  new_date: string; // ISO date string (YYYY-MM-DD)
}

export interface WorkoutCompletionMarkCreate {
  date: string; // ISO date string (YYYY-MM-DD)
}

export interface WorkoutCompletionMarkResponse {
  id: number;
  workout_id: number;
  user_id: number;
  date: string;
  completed_at: string;
}

export interface PlanWizardRequest {
  weekly_distance: string;
  comfortable_pace: string;
  target_distance: string;
  competition_date: string;
  has_specific_goal: boolean;
  preferred_workout_days: number[];
}

export interface PlanWizardResponse {
  complexity: number;
  competition_type: CompetitionType;
  competition_date: string;
  plan_id: number;
}

export interface WeeklyWorkoutCountRequest {
  weekly_distance: string;
  comfortable_pace: string;
  target_distance: string;
  competition_date: string;
  has_specific_goal: boolean;
}

export interface WeeklyWorkoutCountResponse {
  max_weekly_workouts: number;
  complexity: number;
  competition_type: CompetitionType;
}

// Типы для администрирования

export enum TariffType {
  TEST = "test",
  TRIAL = "trial", 
  PRO = "pro"
}

export interface AdminUser {
  id: number;
  uin: string;
  email: string;
  first_name?: string;
  last_name?: string;
  is_active: boolean;
  tariff_type?: TariffType;
  tariff_name?: string;
  created_at: string;
}

export interface UserTariffUpdate {
  user_id: number;
  tariff_type: TariffType;
}

export interface Tariff {
  id: number;
  name: string;
  type: TariffType;
  view_full_plan: boolean;
  view_two_weeks: boolean;
  created_at: string;
  updated_at: string;
}

export interface TariffUpdate {
  view_full_plan: boolean;
  view_two_weeks: boolean;
}

export interface TariffsUpdateRequest {
  test: TariffUpdate;
  trial: TariffUpdate;
  pro: TariffUpdate;
}

export interface WorkoutCoefficients {
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

export interface WorkoutCoefficientsUpdate {
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
}