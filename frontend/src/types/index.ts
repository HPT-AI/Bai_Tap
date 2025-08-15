// Common types for Math Service Frontend

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: 'user' | 'premium_user' | 'admin';
  balance: number;
  created_at: string;
  updated_at: string;
}

export interface MathProblem {
  id: string;
  problem_type: 'quadratic' | 'system' | 'calculus' | 'linear';
  problem_text: string;
  solution: string;
  step_by_step: string[];
  price: number;
  created_at: string;
}

export interface Transaction {
  id: string;
  user_id: string;
  amount: number;
  payment_method: 'vnpay' | 'momo' | 'zalopay';
  status: 'pending' | 'completed' | 'failed';
  created_at: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  errors?: string[];
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

