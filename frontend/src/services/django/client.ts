/**
 * Django API client — centralized fetch wrapper.
 * - Uses Bearer tokens for JWT auth (stored in localStorage).
 * - Implements automatic token refresh on 401.
 *
 * Toggle Django mode via VITE_USE_DJANGO_API=true in .env.
 * Override base URL via VITE_API_BASE_URL.
 */

export const DJANGO_CONFIG = {
  baseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  enabled: import.meta.env.VITE_USE_DJANGO_API === 'true',
};

export const AUTH_KEYS = {
  ACCESS: 'tha_access_token',
  REFRESH: 'tha_refresh_token',
  USER: 'tha_user_data',
};

export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

export class ApiError extends Error {
  status: number;
  data: unknown;
  constructor(status: number, message: string, data?: unknown) {
    super(message);
    this.status = status;
    this.data = data;
  }
}

interface FetchOpts {
  method?: HttpMethod;
  body?: unknown;
  headers?: Record<string, string>;
  signal?: AbortSignal;
  /** Set false for endpoints that don't require auth. */
  requireAuth?: boolean;
}

// Token management helpers
export const tokenStorage = {
  getAccess: () => localStorage.getItem(AUTH_KEYS.ACCESS),
  getRefresh: () => localStorage.getItem(AUTH_KEYS.REFRESH),
  saveTokens: (access: string, refresh?: string) => {
    localStorage.setItem(AUTH_KEYS.ACCESS, access);
    if (refresh) localStorage.setItem(AUTH_KEYS.REFRESH, refresh);
  },
  clearTokens: () => {
    localStorage.removeItem(AUTH_KEYS.ACCESS);
    localStorage.removeItem(AUTH_KEYS.REFRESH);
    localStorage.removeItem(AUTH_KEYS.USER);
  },
};

let isRefreshing = false;
let refreshSubscribers: ((token: string) => void)[] = [];

function onTokenRefreshed(token: string) {
  refreshSubscribers.forEach((callback) => callback(token));
  refreshSubscribers = [];
}

function addRefreshSubscriber(callback: (token: string) => void) {
  refreshSubscribers.push(callback);
}

/**
 * Centralized API call with automatic logout and refresh.
 */
export async function apiFetch<T = unknown>(
  endpoint: string,
  opts: FetchOpts = {}
): Promise<T> {
  const { method = 'GET', body, headers = {}, signal, requireAuth = true } = opts;

  const url = `${DJANGO_CONFIG.baseUrl}${endpoint.startsWith('/') ? '' : '/'}${endpoint}`;
  
  const getHeaders = () => {
    const h: Record<string, string> = {
      Accept: 'application/json',
      ...(body !== undefined ? { 'Content-Type': 'application/json' } : {}),
      ...headers,
    };
    
    if (requireAuth) {
      const token = tokenStorage.getAccess();
      if (token) {
        h['Authorization'] = `Bearer ${token}`;
      }
    }
    return h;
  };

  const performFetch = async (currentHeaders: Record<string, string>) => {
    const init: RequestInit = {
      method,
      signal,
      headers: currentHeaders,
    };

    if (body !== undefined) {
      init.body = typeof body === 'string' ? body : JSON.stringify(body);
    }

    try {
      return await fetch(url, init);
    } catch (err) {
      throw new ApiError(0, 'Network error — is the Django backend reachable?', err);
    }
  };

  let res = await performFetch(getHeaders());

  // Handle Token Refresh
  if (res.status === 401 && requireAuth && tokenStorage.getRefresh()) {
    if (!isRefreshing) {
      isRefreshing = true;
      try {
        const refreshRes = await fetch(`${DJANGO_CONFIG.baseUrl}/auth/token/refresh/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ refresh: tokenStorage.getRefresh() }),
        });

        if (refreshRes.ok) {
          const { access } = await refreshRes.json();
          tokenStorage.saveTokens(access);
          onTokenRefreshed(access);
          isRefreshing = false;
          // Retry the request
          res = await performFetch(getHeaders());
        } else {
          // Refresh failed
          tokenStorage.clearTokens();
          window.dispatchEvent(new CustomEvent('auth:unauthorized'));
          isRefreshing = false;
        }
      } catch (err) {
        isRefreshing = false;
        tokenStorage.clearTokens();
        window.dispatchEvent(new CustomEvent('auth:unauthorized'));
      }
    } else {
      // Wait for the ongoing refresh
      return new Promise<T>((resolve, reject) => {
        addRefreshSubscriber(async (newToken) => {
          try {
            const retryRes = await performFetch({
              ...getHeaders(),
              'Authorization': `Bearer ${newToken}`,
            });
            resolve(await handleResponse<T>(retryRes));
          } catch (err) {
            reject(err);
          }
        });
      });
    }
  }

  return await handleResponse<T>(res);
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (res.status === 204) return undefined as T;

  const contentType = res.headers.get('content-type') || '';
  const data = contentType.includes('application/json')
    ? await res.json().catch(() => null)
    : await res.text().catch(() => null);

  if (!res.ok) {
    if (res.status === 401) {
      window.dispatchEvent(new CustomEvent('auth:unauthorized'));
    }
    if (res.status === 403) {
      window.dispatchEvent(new CustomEvent('auth:forbidden'));
    }
    const message =
      (data && typeof data === 'object' && (data as any).detail) ||
      (data && typeof data === 'object' && (data as any).message) ||
      (typeof data === 'string' ? data : null) ||
      `Request failed with status ${res.status}`;
    throw new ApiError(res.status, message, data);
  }

  return data as T;
}

export const http = {
  get: <T>(endpoint: string, opts?: Omit<FetchOpts, 'method' | 'body'>) =>
    apiFetch<T>(endpoint, { ...opts, method: 'GET' }),
  post: <T>(endpoint: string, body?: unknown, opts?: Omit<FetchOpts, 'method' | 'body'>) =>
    apiFetch<T>(endpoint, { ...opts, method: 'POST', body }),
  put: <T>(endpoint: string, body?: unknown, opts?: Omit<FetchOpts, 'method' | 'body'>) =>
    apiFetch<T>(endpoint, { ...opts, method: 'PUT', body }),
  patch: <T>(endpoint: string, body?: unknown, opts?: Omit<FetchOpts, 'method' | 'body'>) =>
    apiFetch<T>(endpoint, { ...opts, method: 'PATCH', body }),
  delete: <T>(endpoint: string, opts?: Omit<FetchOpts, 'method' | 'body'>) =>
    apiFetch<T>(endpoint, { ...opts, method: 'DELETE' }),
};
