export interface User {
  id: number;
  uin: string;
  email: string;
  first_name?: string;
  last_name?: string;
  is_active: boolean;
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