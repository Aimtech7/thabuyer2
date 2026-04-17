/**
 * API Abstraction Layer (Hybrid)
 *
 * Routes data access to either:
 *   - Django backend (when VITE_USE_DJANGO_API=true)
 *   - Mock services (default, for local UI dev)
 *
 * Components import ONLY from this file. To migrate an endpoint to Django,
 * replace the mock call below with the corresponding djangoX.* call.
 */
import { mockProducts_service } from './mock/mockProducts';
import { mockPricing } from './mock/mockPricing';
import { mockAI } from './mock/mockAI';
import { mockOrders } from './mock/mockOrders';
import {
  DJANGO_CONFIG,
  djangoProducts,
  djangoCart,
  djangoOrders,
} from './django';
import type {
  SearchFilters,
  AIRecommendation,
  Review,
  CartItem,
  DeliveryAddress,
  Order,
} from '@/types';

const useDjango = DJANGO_CONFIG.enabled;

// Helper to transform Django product to Frontend product + listings
const transformProduct = (p: any): Product & { listings: StoreListing[] } => {
  const images = p.images?.map((img: any) => img.image) || [];
  return {
    id: p.id,
    name: p.name,
    description: p.description,
    category: p.category_name || p.category,
    images: images,
    sku: p.SKU,
    createdAt: p.created_at,
    listings: [
      {
        id: `listing-${p.id}`,
        productId: p.id,
        sellerId: p.seller,
        storeName: p.seller_name || p.seller_business || 'Unknown Store',
        price: parseFloat(p.price),
        stock: p.stock_qty,
        sellerRating: p.avg_rating || 0,
        isLowestPrice: true,
      },
    ],
  };
};

export const api = {
  // ─── Products ────────────────────────────────────────────────
  getProducts: async (filters?: SearchFilters) => {
    if (useDjango) {
      const resp = await djangoProducts.list({
        search: filters?.query,
        category: filters?.category,
        // Sort mapping can be added if backend supports it
      });
      // For now, return flat list; UI handles each item as a product with 1 listing
      return resp.results.map(transformProduct);
    }
    return mockProducts_service.getProducts(filters);
  },
  getProduct: async (id: string) => {
    if (useDjango) {
      const p = await djangoProducts.get(id);
      return transformProduct(p);
    }
    return mockProducts_service.getProduct(id);
  },
  getStores: () => mockProducts_service.getStores(),
  getTopStores: () => mockProducts_service.getTopStores(),
  getStore: (id: string) => mockProducts_service.getStore(id),
  getReviews: (productId: string) =>
    useDjango ? djangoProducts.reviews(productId) : mockProducts_service.getReviews(productId),
  addReview: (review: Omit<Review, 'id' | 'createdAt'>) => mockProducts_service.addReview(review),
  getPriceHistory: (productId: string) => mockProducts_service.getPriceHistory(productId),
  getSellerProducts: (sellerId: string) =>
    useDjango ? djangoSeller.getProducts().then(r => r.data.map(transformProduct)) : mockProducts_service.getSellerProducts(sellerId),
  getSellerMetrics: () =>
    useDjango ? djangoSeller.getDashboard().then(r => r.data) : mockProducts_service.getSellerMetrics(),
  getAdminMetrics: () => mockProducts_service.getAdminMetrics(),
  getAdminUsers: () => mockProducts_service.getAdminUsers(),

  // ─── Pricing ─────────────────────────────────────────────────
  comparePrices: (productId: string) =>
    useDjango 
      ? djangoProducts.listings(productId).then(res => res.map((l: any) => ({
          id: l.id,
          productId: l.product_id,
          sellerId: l.seller_id,
          storeName: l.seller_name,
          price: parseFloat(l.price),
          stock: l.stock_qty,
          sellerRating: l.seller_rating,
          isLowestPrice: l.is_lowest_price
        })))
      : mockPricing.comparePrices(productId),
  getLowestPrice: (productId: string) => mockPricing.getLowestPriceListing(productId),
  getPriceDrops: () => mockPricing.getPriceDrops(),

  // ─── AI ──────────────────────────────────────────────────────
  getAIRecommendation: (productId: string): Promise<AIRecommendation | null> =>
    mockAI.getRecommendation(productId),
  getBestValue: (productId: string) => mockAI.getBestValue(productId),
  getPersonalizedRecommendations: (limit?: number) => mockAI.getPersonalizedRecommendations(limit),

  // ─── Orders ──────────────────────────────────────────────────
  getOrders: (userId?: string) =>
    useDjango ? djangoOrders.list() : mockOrders.getOrders(userId),
  getOrder: (orderId: string) =>
    useDjango ? djangoOrders.get(orderId) : mockOrders.getOrder(orderId),
  checkout: (
    items: CartItem[],
    address: DeliveryAddress,
    paymentMethod: string,
    userId: string
  ): Promise<Order> => {
    if (useDjango) {
      // Stringify address for backend TextField
      const addressStr = `${address.fullName}, ${address.street}, ${address.city}, ${address.state} ${address.zipCode}, ${address.country}. Ph: ${address.phone}`;
      return djangoOrders
          .checkout({ 
            shipping_address: addressStr, 
            payment_ref: paymentMethod === 'stripe' ? 'pending_stripe' : 'cod'
          })
          .then((r) => r.data);
    }
    return mockOrders.checkout(items, address, paymentMethod, userId);
  },
  cancelOrder: (orderId: string) =>
    useDjango ? djangoOrders.cancel(orderId) : mockOrders.cancelOrder(orderId),
  getSellerOrders: (sellerId: string) => mockOrders.getSellerOrders(sellerId),
  getOrderStats: () => mockOrders.getOrderStats(),

  // ─── Cart ────
  cart: useDjango ? djangoCart : null,
};
