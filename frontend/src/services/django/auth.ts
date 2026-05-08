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
  commission_accepted?: boolean;
}

interface AuthResponse {
  status: string;
  message?: string;
  requires_2fa?: boolean;
  temp_token?: string;
  data?: {
    access: string;
    refresh: string;
    user: User;
  };
}

const mapUser = (u: any): User => ({
  id: String(u.id),
  fullName: u.name || '',
  email: u.email || '',
  phone: u.phone || '',
  role: u.role as UserRole,
  isVerified: !!u.verified,
  isActive: u.is_active !== false,
  is2faEnabled: !!u.is_2fa_enabled,
  createdAt: u.date_joined || new Date().toISOString(),
});

export const djangoAuth = {
  login: async (payload: LoginPayload) => {
    const res = await http.post<AuthResponse>('/auth/login/', payload, { requireAuth: false });
    
    if (res.requires_2fa) {
      return { requires2FA: true, tempToken: res.temp_token };
    }
    
    if (!res.data) throw new Error('Invalid response');
    
    const { access, refresh, user: rawUser } = res.data;
    const user = mapUser(rawUser);
    tokenStorage.saveTokens(access, refresh);
    localStorage.setItem(AUTH_KEYS.USER, JSON.stringify(user));
    return { user, requires2FA: false };
  },

  login2FA: async (tempToken: string, code: string) => {
    const res = await http.post<AuthResponse>('/auth/login/2fa/', { temp_token: tempToken, otp: code }, { requireAuth: false });
    if (!res.data) throw new Error('Invalid response');
    
    const { access, refresh, user: rawUser } = res.data;
    const user = mapUser(rawUser);
    tokenStorage.saveTokens(access, refresh);
    localStorage.setItem(AUTH_KEYS.USER, JSON.stringify(user));
    return { user };
  },

  register: async (payload: RegisterPayload) => {
    const res = await http.post<AuthResponse>('/auth/register/', payload, { requireAuth: false });
    if (!res.data) throw new Error('Invalid response');
    
    const { access, refresh, user: rawUser } = res.data;
    const user = mapUser(rawUser);
    tokenStorage.saveTokens(access, refresh);
    localStorage.setItem(AUTH_KEYS.USER, JSON.stringify(user));
    return { user };
  },

  setup2FA: async () => {
    const res = await http.post<{ secret: string, provisioning_uri: string }>('/auth/2fa/setup/', {});
    return res;
  },

  verify2FASetup: async (code: string) => {
    const res = await http.post<{ status: string, message: string }>('/auth/2fa/verify-setup/', { otp: code });
    return res;
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

  me: async () => {
    const rawUser = await http.get<any>('/auth/profile/');
    return mapUser(rawUser);
  },
};
