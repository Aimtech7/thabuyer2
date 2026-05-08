# Implementation Plan: SRS v2.0 Missing Features

## Goal Description
The objective of this plan is to implement all missing features identified in the `SRS_Ecommerce_Platform_v3.docx` (v2.0) across the backend (Django) and frontend (React/Next.js) to bring the multi-store e-commerce platform up to the commercial release standards.

---

## Proposed Changes

### 1. Authentication & Onboarding (FR-01)
*   **Two-Factor Authentication (2FA) (FR-01.8)**: 
    *   *Backend:* Add SMS/TOTP logic to the `users` app.
    *   *Frontend:* Build the 2FA setup and verification UI flows.
*   **Commission Policy Agreement (FR-01.7)**: 
    *   *Backend:* Update seller registration to require a `commission_accepted` flag.
    *   *Frontend:* Update the onboarding UI to include a digital sign-off of the Commission Policy.
*   **Assisted Upload Service (FR-02.10)**: 
    *   *Backend/Frontend:* Create an admin tool for the concierge bulk upload of a seller's initial product catalog from email attachments.

### 2. Seller Hub & Catalogue Management (FR-02)
*   **Excel Bulk Upload (FR-02.3, FR-02.4)**: 
    *   *Backend:* Finalize the `.xlsx` parser in `products/views.py`. Implement strict row-level validation and generate downloadable error reports for invalid rows.
    *   *Frontend:* Build the file upload UI and error report review screen.
*   **Price Freshness (FR-02.7)**: 
    *   *Backend:* Add a periodic task (Celery) to check the `last_updated` date of products and flag prices older than 30 days.
    *   *Frontend:* Add a UI prompt/banner for sellers to confirm prices.
*   **Catalogue Analytics (FR-02.8)**: 
    *   *Backend:* Build a tracking model for views/clicks/conversions in `sellers/models.py` and expose an analytics API.
    *   *Frontend:* Build an analytics dashboard for sellers.
*   **Custom Collections & Promos (FR-02.9)**: 
    *   *Backend:* Add models for custom collections and date-bound promotional pricing in `products`.
    *   *Frontend:* Create the seller UI to manage collections and promos.

### 3. Buyer Search, Price Intelligence & Comparison (FR-03 & UC-14)
*   **Price History Graph (FR-03.9)**: 
    *   *Backend:* Create a `PriceHistory` model to track price changes over time. Expose an API endpoint.
    *   *Frontend:* Build a 90-day trend graph UI component for product detail pages.
*   **Price-Drop Alerts (FR-03.10 / UC-14)**: 
    *   *Backend:* Create a `PriceAlert` model. Add a background task that triggers email notifications when a price drops below a user's threshold.
    *   *Frontend:* Build the subscription UI on product pages.
*   **AI Buying Tool UI (UC-07)**: 
    *   *Backend:* Integrate the existing scoring logic from `ai_engine/engine.py` into the main search API.
    *   *Frontend:* Surface the "Best Value" badge and the natural-language explanation in the search results.

### 4. Shopping Cart & Checkout (FR-04)
*   **Secondary Payment Fallback (FR-04.4)**: 
    *   *Backend:* Integrate a secondary payment provider in `orders/views.py` and implement automatic failover logic if the primary gateway fails or times out.
*   **Guest Checkout (FR-04.8)**: 
    *   *Backend:* Adjust cart and checkout endpoints to support session-based, unauthenticated checkout.
    *   *Frontend:* Modify routing and UI to allow checkout without an account.

### 5. Social & Community (FR-06)
*   **Community Forums (FR-06.1)**: 
    *   *Backend:* Create `ForumThread` and `ForumPost` models with upvote/reply functionality.
    *   *Frontend:* Build the product-linked discussion board UI.
*   **Follow Stores (FR-06.6)**: 
    *   *Backend:* Create a `StoreFollow` model and notification trigger logic for new listings.
    *   *Frontend:* Build the UI to follow/unfollow stores.

### 6. Static Pages & Admin Suite (FR-07 & FR-08)
*   **Supplier Directory (FR-07.5)**: 
    *   *Backend/Frontend:* Create the Supplier model, API, and the dynamic directory page.
*   **Help Centre Integrations (FR-07.6)**: 
    *   *Frontend:* Integrate the contact form with a ticketing backend and add a live chat widget.
*   **Admin Alerts (FR-08.5)**: 
    *   *Backend:* Add automated system alerts to admins when sellers fail the 30-day price confirmation.
*   **SEO Management Tools (FR-08.6)**: 
    *   *Backend:* Create a model to store SEO metadata (titles, descriptions, canonical URLs).
    *   *Frontend:* Build the admin dashboard UI to manage these SEO tags.

---

## Verification Plan

### Automated Tests
- Write unit tests for all new models (`PriceHistory`, `PriceAlert`, `ForumThread`, `StoreFollow`).
- Write integration tests for the fallback payment gateway logic and Excel bulk upload parsing.

### Manual Verification
- Test the 2FA flow from registration to successful login.
- Upload valid and invalid `.xlsx` files and verify the generated error reports.
- Trigger the Price-Drop alert manually via the shell to ensure emails are dispatched.
- Perform a guest checkout flow in the browser.
