/**
 * Auth API Client
 * Handles authentication with Supabase
 */

import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

export const supabase = createClient(supabaseUrl, supabaseKey);

// Types
export interface User {
  id: string;
  email: string;
  full_name?: string;
  monthly_income?: number;
  financial_goals?: string[];
  risk_tolerance?: 'conservative' | 'moderate' | 'aggressive';
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface Session {
  user: User;
  token: string;
}

// API Functions

export const authAPI = {
  /**
   * Register a new user
   */
  register: async (request: RegisterRequest): Promise<Session> => {
    const { data, error } = await supabase.auth.signUp({
      email: request.email,
      password: request.password,
      options: {
        data: {
          full_name: request.full_name,
        },
      },
    });

    if (error) throw error;
    if (!data.user || !data.session) throw new Error('Registration failed');

    // Store token
    localStorage.setItem('token', data.session.access_token);

    return {
      user: {
        id: data.user.id,
        email: data.user.email!,
        full_name: request.full_name,
      },
      token: data.session.access_token,
    };
  },

  /**
   * Login existing user
   */
  login: async (request: LoginRequest): Promise<Session> => {
    const { data, error } = await supabase.auth.signInWithPassword({
      email: request.email,
      password: request.password,
    });

    if (error) throw error;
    if (!data.user || !data.session) throw new Error('Login failed');

    // Store token
    localStorage.setItem('token', data.session.access_token);

    return {
      user: {
        id: data.user.id,
        email: data.user.email!,
        full_name: data.user.user_metadata?.full_name,
      },
      token: data.session.access_token,
    };
  },

  /**
   * Logout current user
   */
  logout: async (): Promise<void> => {
    const { error } = await supabase.auth.signOut();
    if (error) throw error;
    localStorage.removeItem('token');
  },

  /**
   * Get current user
   */
  getCurrentUser: async (): Promise<User | null> => {
    const { data: { user }, error } = await supabase.auth.getUser();

    if (error || !user) return null;

    return {
      id: user.id,
      email: user.email!,
      full_name: user.user_metadata?.full_name,
    };
  },

  /**
   * Update user profile
   */
  updateProfile: async (updates: Partial<User>): Promise<User> => {
    const { data, error } = await supabase.auth.updateUser({
      data: updates,
    });

    if (error) throw error;
    if (!data.user) throw new Error('Update failed');

    return {
      id: data.user.id,
      email: data.user.email!,
      ...data.user.user_metadata,
    };
  },

  /**
   * Get auth session
   */
  getSession: async () => {
    const { data, error } = await supabase.auth.getSession();
    if (error) throw error;
    return data.session;
  },
};
