import { http } from './client';
import type { Order, DeliveryAddress } from '@/types';

export interface CheckoutPayload {
  shipping_address: string;
  notes?: string;
  coupon_code?: string;
  payment_ref?: string;
}

export interface CheckoutResponse {
  status: string;
  message: string;
  client_secret: string | null;
  data: Order;
}

interface ApiResponse<T> {
  status: string;
  data: T;
}

export const djangoOrders = {
  list: () => http.get<ApiResponse<Order[]>>('/orders/').then(res => res.data),
  get: (id: string) => http.get<ApiResponse<Order>>(`/orders/${id}/`).then(res => res.data),
  checkout: (payload: CheckoutPayload) =>
    http.post<CheckoutResponse>('/orders/checkout/', payload),
  cancel: (id: string) => http.post<ApiResponse<Order>>(`/orders/${id}/cancel/`).then(res => res.data),
};
