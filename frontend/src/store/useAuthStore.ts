import { create } from 'zustand';

export type AuthStatus = 'PENDING' | 'ACTIVE' | 'EXPIRED';

export interface User {
  id: string;
  name: string;
  email: string;
  // Easily extendable
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  status: AuthStatus;
  login: (user: User, token: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  isAuthenticated: false,
  status: 'PENDING',
  login: (user, token) => set({ user, token, isAuthenticated: true, status: 'ACTIVE' }),
  logout: () => set({ user: null, token: null, isAuthenticated: false, status: 'EXPIRED' }),
}));
