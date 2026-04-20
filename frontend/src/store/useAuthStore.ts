import { create } from 'zustand';
import { api } from '../services/api';

export type AuthStatus = 'PENDING' | 'ACTIVE' | 'EXPIRED';

export interface User {
  id: string;
  name: string;
  username?: string;
  email: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  status: AuthStatus;
  
  // Temporary storage to map register -> verify-email flow
  tempEmail: string | null;

  // Existing sync update handlers
  setAuth: (user: User, token: string) => void;
  logout: () => void;
  setTempEmail: (email: string) => void;

  // Async API Actions
  registerUser: (data: any) => Promise<void>;
  verifyOtp: (email: string, otp: string) => Promise<void>;
  loginUser: (identifier: string, password: string) => Promise<void>;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  token: null,
  isAuthenticated: false,
  status: 'PENDING',
  tempEmail: null,

  setAuth: (user, token) => set({ user, token, isAuthenticated: true, status: 'ACTIVE' }),
  logout: () => set({ user: null, token: null, isAuthenticated: false, status: 'EXPIRED', tempEmail: null }),
  setTempEmail: (email) => set({ tempEmail: email }),

  registerUser: async (data: any) => {
    // Ex. payload: { fullName, username, email, password }
    await api.post('/auth/register', data);
    set({ tempEmail: data.email });
  },

  verifyOtp: async (email: string, otp: string) => {
    // The backend should return the authentication result alongside token
    const response = await api.post('/auth/verify-email', { email, otp });
    const { user, token } = response.data;
    set({ user, token, isAuthenticated: true, status: 'ACTIVE', tempEmail: null });
  },

  loginUser: async (identifier: string, password: string) => {
    const response = await api.post('/auth/login', { identifier, password });
    const { user, token } = response.data;
    set({ user, token, isAuthenticated: true, status: 'ACTIVE', tempEmail: null });
  }
}));
