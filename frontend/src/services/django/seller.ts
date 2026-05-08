/**
 * Seller service for Django.
 */
import { http } from './client';
import type { Product, Order, Review } from '@/types';

export interface SellerDashboardMetrics {
  profile: any;
  total_products: number;
  total_orders: number;
  total_revenue: string;
  pending_orders: number;
  recent_reviews: Review[];
  total_views?: number;
  total_clicks?: number;
  stale_products_count?: number;
}

interface ApiResponse<T> {
  status: string;
  data: T;
}

export const djangoSeller = {
  dashboard: () =>
    http.get<ApiResponse<SellerDashboardMetrics>>('/seller/dashboard/').then(res => ({
      totalProducts: res.data.total_products,
      totalOrders: res.data.total_orders,
      revenue: parseFloat(res.data.total_revenue),
      pendingOrders: res.data.pending_orders,
      recentReviews: res.data.recent_reviews,
      profile: res.data.profile,
      totalViews: res.data.total_views || 0,
      totalClicks: res.data.total_clicks || 0,
      staleProductsCount: res.data.stale_products_count || 0,
    })),

  products: () =>
    http.get<ApiResponse<Product[]>>('/seller/products/').then(res => res.data),

  getProfile: () =>
    http.get<ApiResponse<any>>('/seller/profile/'),

  updateProfile: (data: any) =>
    http.put<ApiResponse<any>>('/seller/profile/', data),

  getCollections: () => http.get('/products/collections/').then(res => res.data),
  createCollection: (data: any) => http.post('/products/collections/', data).then(res => res.data),
  updateCollection: (id: string, data: any) => http.put(`/products/collections/${id}/`, data).then(res => res.data),
  deleteCollection: (id: string) => http.delete(`/products/collections/${id}/`).then(res => res.data),

  getPromoPricing: () => http.get('/promotions/promopricing/').then(res => res.data),
  createPromoPricing: (data: any) => http.post('/promotions/promopricing/', data).then(res => res.data),
  deletePromoPricing: (id: string) => http.delete(`/promotions/promopricing/${id}/`).then(res => res.data),

  bulkUploadProducts: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return http.post('/products/bulk-upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }).then(res => res.data);
  },
};
