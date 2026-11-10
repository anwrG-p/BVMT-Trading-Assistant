import React, { createContext, useState, useEffect, ReactNode } from 'react';
import mockAuthService from './mockAuthService';
import { User } from '../types';

export interface AuthContextType {
  currentUser: User | null;
  login: (email: string, password: string) => Promise<{ user: User | null; error: string | null }>;
  register: (email: string, password: string, name: string) => Promise<{ user: User | null; error: string | null }>;
  logout: () => void;
  loading: boolean;
}

export const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const user = mockAuthService.getCurrentUser();
    setCurrentUser(user);
    setLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    const { user, error } = await mockAuthService.login(email, password);
    if (user) {
      setCurrentUser(user);
    }
    return { user, error };
  };

  const register = async (email: string, password: string, name: string) => {
    const { user, error } = await mockAuthService.register(email, password, name);
    if (user) {
      const loginResult = await mockAuthService.login(email, password);
      if (loginResult.user) {
        setCurrentUser(loginResult.user);
      }
    }
    return { user, error };
  };

  const logout = () => {
    mockAuthService.logout();
    setCurrentUser(null);
  };

  const value: AuthContextType = {
    currentUser,
    login,
    register,
    logout,
    loading
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};
