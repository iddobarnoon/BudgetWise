"use client";

import React, { createContext, useContext, useEffect, useState } from 'react';
import { authAPI, User } from '@/lib/api';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName: string) => Promise<void>;
  logout: () => Promise<void>;
  updateUser: (updates: Partial<User>) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for existing session on mount
    checkUser();
  }, []);

  const checkUser = async () => {
    try {
      const currentUser = await authAPI.getCurrentUser();
      setUser(currentUser);
    } catch (error) {
      console.error('Failed to get current user:', error);
    } finally {
      setLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    const session = await authAPI.login({ email, password });
    setUser(session.user);
  };

  const register = async (email: string, password: string, fullName: string) => {
    const session = await authAPI.register({ email, password, full_name: fullName });
    setUser(session.user);
  };

  const logout = async () => {
    await authAPI.logout();
    setUser(null);
  };

  const updateUser = async (updates: Partial<User>) => {
    const updatedUser = await authAPI.updateProfile(updates);
    setUser(updatedUser);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, updateUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
