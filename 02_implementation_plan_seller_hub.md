# Module 2: Seller Hub & Catalogue Management (FR-02) Implementation Plan

This plan outlines the integration of the next batch of features for the Seller module, as defined in SRS v2.0 (FR-02). The focus is on Catalogue Management, Analytics, and Promotions.

## User Review Required

> [!IMPORTANT]
> **Celery Infrastructure:** The Price Freshness feature requires a running Celery worker to execute the background checks. Please ensure Redis/RabbitMQ and the Celery worker process are configured in your development environment (`celery -A core worker -l info`).

> [!NOTE]
> **Analytics Tracking:** We will track "views" directly when a user hits the `ProductDetailView`. For "clicks" (e.g., clicking on a product in a search result), we can either infer them from views or add a dedicated `/api/products/<id>/click/` endpoint. The plan assumes adding a dedicated click endpoint for accuracy.

## Open Questions

1. **Celery Beat:** Do you have `celery-beat` configured for periodic tasks, or should I add the schedule configuration in `core/celery.py`?
2. **Promotions UI:** Should the "Promotions & Collections" UI be housed inside the main `SellerDashboard.tsx` via tabs, or would you prefer dedicated route pages (e.g., `/seller/promotions`) to prevent the dashboard component from becoming too large?

---

## Proposed Changes

### Backend: Models & Tasks

#### [MODIFY] `backend/products/models.py`
- Add `views_count = models.PositiveIntegerField(default=0)` and `clicks_count = models.PositiveIntegerField(default=0)` to the `Product` model.
- **[NEW]** Add a `Collection` model:
  - `name`, `slug`, `seller` (ForeignKey), `products` (ManyToManyField), `is_active`, `created_at`.

#### [MODIFY] `backend/promotions/models.py`
- **[NEW]** Add a `PromoPricing` model:
  - `product` (OneToOne/ForeignKey), `promo_price`, `start_date`, `end_date`, `is_active`.

#### [NEW] `backend/products/tasks.py`
- Create a Celery task `check_price_freshness`:
  - Scans for `Product` instances where `updated_at` is older than 30 days.
  - Dispatches an in-app `Notification` to the respective seller alerting them to update their prices.

---

### Backend: API Views & Serializers

#### [MODIFY] `backend/products/views.py`
- Update `ProductDetailView` to increment the `views_count` upon retrieval.
- **[NEW]** Create `ProductClickView` to increment `clicks_count` via a simple POST request.
- **[NEW]** Create `CollectionListCreateView` and `CollectionDetailView` for sellers to manage collections.

#### [MODIFY] `backend/promotions/views.py`
- **[NEW]** Create `PromoPricingListCreateView` to allow sellers to attach date-bound promo prices to their products.

#### [MODIFY] `backend/sellers/views.py`
- Update `SellerDashboardView` to return:
  - Total catalogue views (Sum of `views_count`).
  - Total catalogue clicks (Sum of `clicks_count`).
  - Count of stale products (`updated_at` > 30 days).

---

### Frontend: Dashboard UI Integration

#### [MODIFY] `frontend/src/services/django/seller.ts`
- Add `bulkUpload(file: File)` method to send multipart `FormData` to the `/api/products/bulk-upload/` endpoint.
- Add methods for `getCollections()`, `createCollection()`, `getPromos()`, and `createPromo()`.
- Update `SellerDashboardMetrics` interface to include `total_views`, `total_clicks`, and `stale_products_count`.

#### [MODIFY] `frontend/src/components/BulkUploadDialog.tsx`
- Refactor to remove the mock `FileReader` CSV parsing.
- Hook up the file upload to `djangoSeller.bulkUpload(file)`.
- Parse the `207 Multi-Status` response and display the exact rows and SKUs that failed backend validation in the error table.

#### [MODIFY] `frontend/src/pages/seller/SellerDashboard.tsx`
- **Metrics Overview:** Add View and Click statistics to the top KPI cards.
- **Price Freshness Alert:** Add a dismissible warning banner if `stale_products_count > 0`, linking to a filtered view of stale products.
- **Tabs Expansion:** Add a `Promotions` tab to manage Custom Collections and Date-Bound Pricing.

## Verification Plan

### Automated Tests
- Run Django tests for `ProductBulkUploadView` ensuring correct parsing of valid/invalid Excel rows.
- Run tests for `check_price_freshness` to ensure it triggers notifications only for products older than 30 days.

### Manual Verification
1. Log in as a Seller.
2. Attempt a Bulk Upload with an intentionally flawed `.xlsx` file and verify the error report renders correctly in the UI.
3. Simulate an old product and verify the "Price Freshness" alert appears.
4. View a product as a buyer and verify the seller's dashboard analytics update in real-time.
