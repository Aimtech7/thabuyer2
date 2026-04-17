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
    })),

  products: () =>
    http.get<ApiResponse<Product[]>>('/seller/products/').then(res => res.data),

  getProfile: () =>
    http.get<ApiResponse<any>>('/seller/profile/'),

  updateProfile: (data: any) =>
    http.put<ApiResponse<any>>('/seller/profile/', data),
};
