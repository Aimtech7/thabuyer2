/**
 * Auth via Django JWT (Bearer Tokens).
 */
import { http, tokenStorage, AUTH_KEYS } from './client';
import type { User, UserRole } from '@/types';

export interface LoginPayload { email: string; password: string }
export interface RegisterPayload {
  email: string;
  password: string;
  password_confirm: string;
  name: string;
  phone: string;
  role: UserRole;
  businessName?: string;
}

interface AuthResponse {
  status: string;
  message: string;
  data: {
    access: string;
    refresh: string;
    user: User;
  };
}

export const djangoAuth = {
  login: async (payload: LoginPayload) => {
    const res = await http.post<AuthResponse>('/auth/login/', payload, { requireAuth: false });
    const { access, refresh, user } = res.data;
    tokenStorage.saveTokens(access, refresh);
    localStorage.setItem(AUTH_KEYS.USER, JSON.stringify(user));
    return { user };
  },

  register: async (payload: RegisterPayload) => {
    const res = await http.post<AuthResponse>('/auth/register/', payload, { requireAuth: false });
    const { access, refresh, user } = res.data;
    tokenStorage.saveTokens(access, refresh);
    localStorage.setItem(AUTH_KEYS.USER, JSON.stringify(user));
    return { user };
  },

  logout: async () => {
    try {
      const refresh = tokenStorage.getRefresh();
      if (refresh) {
        await http.post('/auth/logout/', { refresh });
      }
    } finally {
      tokenStorage.clearTokens();
    }
  },

  me: () => http.get<User>('/auth/profile/'),
};
