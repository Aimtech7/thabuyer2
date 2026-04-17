import { http } from './client';
import type { CartItem } from '@/types';

interface ApiResponse<T> {
  status: string;
  data: T;
  message?: string;
}

export const djangoCart = {
  get: () => http.get<ApiResponse<any>>('/cart/').then(res => res.data),
  add: (productId: string, quantity = 1) =>
    http.post<ApiResponse<any>>('/cart/add/', { product_id: productId, quantity }).then(res => res.data),
  remove: (productId: string) => 
    http.delete<ApiResponse<any>>('/cart/remove/', { data: { product_id: productId } }),
  clear: () => http.delete<ApiResponse<any>>('/cart/clear/'),
};
