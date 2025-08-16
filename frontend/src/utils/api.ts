// API utility functions for Math Service Frontend

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  // User Service
  USER_SERVICE: process.env.NEXT_PUBLIC_USER_SERVICE_URL || 'http://localhost:8001',
  LOGIN: '/auth/login',
  REGISTER: '/auth/register',
  PROFILE: '/users/profile',

  // Payment Service
  PAYMENT_SERVICE: process.env.NEXT_PUBLIC_PAYMENT_SERVICE_URL || 'http://localhost:8002',
  TRANSACTIONS: '/transactions',
  PAYMENT_METHODS: '/payment-methods',

  // Math Solver Service
  MATH_SERVICE: process.env.NEXT_PUBLIC_MATH_SOLVER_SERVICE_URL || 'http://localhost:8003',
  SOLVE_PROBLEM: '/solve',
  PROBLEM_HISTORY: '/problems/history',

  // Content Service
  CONTENT_SERVICE: process.env.NEXT_PUBLIC_CONTENT_SERVICE_URL || 'http://localhost:8004',
  PAGES: '/pages',
  FAQS: '/faqs',

  // Admin Service
  ADMIN_SERVICE: process.env.NEXT_PUBLIC_ADMIN_SERVICE_URL || 'http://localhost:8005',
  DASHBOARD: '/dashboard',
  USERS: '/users',
};

export class ApiClient {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;

    // Get token from localStorage if available
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('access_token');
    }
  }

  setToken(token: string) {
    this.token = token;
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', token);
    }
  }

  clearToken() {
    this.token = null;
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
    }
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`;
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || `HTTP Error: ${response.status}`);
    }

    return response.json();
  }

  // GET request
  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' });
  }

  // POST request
  async post<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  // PUT request
  async put<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  // DELETE request
  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }
}

// Default API client instance
export const apiClient = new ApiClient();

// Service-specific API clients
export const userApiClient = new ApiClient(API_ENDPOINTS.USER_SERVICE);
export const paymentApiClient = new ApiClient(API_ENDPOINTS.PAYMENT_SERVICE);
export const mathApiClient = new ApiClient(API_ENDPOINTS.MATH_SERVICE);
export const contentApiClient = new ApiClient(API_ENDPOINTS.CONTENT_SERVICE);
export const adminApiClient = new ApiClient(API_ENDPOINTS.ADMIN_SERVICE);
