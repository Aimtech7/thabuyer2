import { http } from './client';
import type { Product, StoreListing, Review } from '@/types';

export interface ProductListParams {
  search?: string;
  category?: string;
  minPrice?: number;
  maxPrice?: number;
  page?: number;
  pageSize?: number;
}

function toQuery(params?: Record<string, unknown>) {
  if (!params) return '';
  const usp = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== '') usp.append(k, String(v));
  });
  const s = usp.toString();
  return s ? `?${s}` : '';
}

export interface PaginatedResponse<T> {
  status: string;
  count: number;
  total_pages: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

interface ApiResponse<T> {
  status: string;
  data: T;
  message?: string;
}

export const djangoProducts = {
  list: (params?: ProductListParams) =>
    http.get<PaginatedResponse<Product>>(
      `/products/${toQuery(params as Record<string, unknown>)}`
    ),
  get: (id: string) =>
    http.get<Product>(`/products/${id}/`), // Standard RetrieveView returns object directly
  listings: (productId: string) =>
    http.get<StoreListing[]>(`/products/${productId}/listings/`), // Standard ListAPIView
  reviews: (productId: string) =>
    http.get<Review[]>(`/products/${productId}/reviews/`),
};
