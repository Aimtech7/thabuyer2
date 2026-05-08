# 🛒 Multi-Store E-Commerce & Price Comparison — Backend API

A **production-ready Django REST Framework** backend for a multi-store e-commerce platform with built-in price comparison, AI-powered buying recommendations, role-based access control, real-time WebSocket notifications, and Stripe-integrated payments.

---

## 📐 Architecture Overview

```
backend/
├── core/             # Settings, URLs, Celery, ASGI, middleware, permissions, exceptions
├── api/              # Central v1 URL router
│
├── users/            # JWT auth, custom User model, RBAC (Buyer/Seller/Admin), 2FA, Google OAuth
├── sellers/          # SellerProfile, dashboard, analytics, verification
├── products/         # Product catalog, categories, images, collections, bulk upload (.xlsx)
├── pricing/          # PriceHistory, PriceAlert, Celery-driven alert checks
├── cart/             # Cart + CartItem, add/remove/clear
├── orders/           # Order lifecycle, checkout (atomic), Stripe payments, EasyPost shipping
├── reviews/          # Reviews (stars + comment), DiscussionThreads + Replies, content reports
├── admin_panel/      # Admin-only user/seller management, analytics, assisted upload
├── ai_engine/        # Multi-factor AI scoring engine + recommendation API
├── promotions/       # Coupons (fixed/percent), promotional pricing per product
├── notifications/    # In-app notifications (REST + WebSocket real-time delivery)
├── wishlists/        # Buyer wishlist — add/remove/clear products
├── messaging/        # Real-time Buyer-Seller chat (WebSockets)
├── analytics/        # Performance reports and data exports (CSV/PDF)
└── shipping/         # Granular shipment tracking and address management
```

---

## 🔧 Tech Stack

| Layer            | Technology                                   |
|------------------|----------------------------------------------|
| Framework        | Django 4.2 + DRF 3.15                        |
| Auth             | JWT (SimpleJWT) + bcrypt hashing             |
| Social Auth      | django-allauth + dj-rest-auth (Google OAuth) |
| 2FA              | pyotp (TOTP — RFC 6238)                      |
| Database         | PostgreSQL (SQLite for local dev)            |
| Task Queue       | Celery 5 + Redis                             |
| Real-Time        | Django Channels + Daphne (WebSocket)         |
| Payments         | Stripe (PaymentIntents + Webhooks)           |
| Shipping         | EasyPost (label generation)                  |
| Static Files     | WhiteNoise (compressed, cached)              |
| API Docs         | drf-spectacular (Swagger + ReDoc)            |
| Testing          | pytest-django + pytest                       |
| Deployment       | Docker + Nginx + Gunicorn                    |

---

## 🚀 Quick Start (Local Development)

### Prerequisites
- Python 3.11+
- PostgreSQL 15+ (or use SQLite for dev)
- Redis (for Celery & WebSockets — optional locally)

### 1. Clone & Setup

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Environment

```bash
copy .env.example .env      # Windows
cp .env.example .env        # macOS/Linux
```

Edit `.env` — for local SQLite dev, leave `DATABASE_URL` blank (defaults to SQLite).

### 3. Run Migrations

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 4. Start the Server

```bash
python manage.py runserver
```

API is live at **http://127.0.0.1:8000/api/v1/**

Interactive docs: **http://127.0.0.1:8000/api/docs/**

---

## 🐳 Docker Deployment (Production)

```bash
# Build and start all services
docker compose up -d --build

# Run migrations inside the container
docker compose exec api python manage.py migrate
docker compose exec api python manage.py createsuperuser
```

Services started:
- **api** → Django/Gunicorn on port 8000
- **nginx** → Reverse proxy on port 80
- **db** → PostgreSQL on port 5432
- **redis** → Redis on port 6379
- **celery_worker** → Background task processor
- **celery_beat** → Periodic task scheduler

---

## 🔌 API Reference

All endpoints are prefixed with `/api/v1/`. Full interactive docs at `/api/docs/`.

### 🔐 Authentication

| Method | Endpoint                    | Description                      | Auth  |
|--------|-----------------------------|----------------------------------|-------|
| POST   | `/auth/register/`           | Register Buyer or Seller         | None  |
| POST   | `/auth/login/`              | Login → JWT tokens               | None  |
| POST   | `/auth/logout/`             | Blacklist refresh token          | JWT   |
| POST   | `/auth/token/refresh/`      | Refresh access token             | JWT   |
| GET    | `/auth/profile/`            | View own profile                 | JWT   |
| PUT    | `/auth/profile/`            | Update own profile               | JWT   |
| POST   | `/auth/google/`             | Google OAuth login               | None  |
| POST   | `/auth/2fa/setup/`          | Generate TOTP secret + QR URI    | JWT   |
| POST   | `/auth/2fa/verify-setup/`   | Verify OTP to enable 2FA         | JWT   |
| POST   | `/auth/2fa/verify-login/`   | OTP check during login flow      | None  |

### 📦 Products

| Method | Endpoint                          | Description                        | Auth   |
|--------|-----------------------------------|------------------------------------|--------|
| GET    | `/products/`                      | List all products (paginated)      | None   |
| POST   | `/products/create/`               | Create a product                   | Seller |
| GET    | `/products/<id>/`                 | Product detail                     | None   |
| PUT    | `/products/<id>/update/`          | Update own product                 | Seller |
| GET    | `/products/<id>/compare/`         | Price comparison table             | None   |
| POST   | `/products/<id>/click/`           | Record product click (analytics)   | None   |
| GET    | `/products/search/?q=`            | Full-text search                   | None   |
| POST   | `/products/bulk-upload/`          | Bulk upload via Excel (.xlsx)      | Seller |
| GET    | `/products/categories/`           | List categories                    | None   |
| GET    | `/products/collections/`          | List seller's collections          | Seller |
| POST   | `/products/collections/`          | Create a collection                | Seller |
| GET    | `/products/collections/<id>/`     | Collection detail                  | Seller |
| PUT    | `/products/collections/<id>/`     | Update collection                  | Seller |
| DELETE | `/products/collections/<id>/`     | Delete collection                  | Seller |

### 🛒 Cart

| Method | Endpoint         | Description              | Auth   |
|--------|------------------|--------------------------|--------|
| GET    | `/cart/`         | View cart                | Buyer  |
| POST   | `/cart/add/`     | Add item (or increment)  | Buyer  |
| DELETE | `/cart/remove/`  | Remove item              | Buyer  |
| DELETE | `/cart/clear/`   | Clear all items          | Buyer  |

### 📋 Orders

| Method | Endpoint                     | Description                    | Auth           |
|--------|------------------------------|--------------------------------|----------------|
| POST   | `/orders/checkout/`          | Checkout from cart             | Buyer          |
| GET    | `/orders/`                   | List own orders                | Buyer          |
| GET    | `/orders/<id>/`              | Order detail                   | Buyer / Admin  |
| PATCH  | `/orders/<id>/status/`       | Update order status            | Seller / Admin |
| POST   | `/orders/<id>/fulfill/`      | Generate shipping label        | Seller / Admin |
| POST   | `/orders/webhook/stripe/`    | Stripe payment webhook         | None (signed)  |

### ⭐ Reviews

| Method | Endpoint                                    | Description                       | Auth        |
|--------|---------------------------------------------|-----------------------------------|-------------|
| POST   | `/reviews/`                                 | Create review (must have ordered) | Buyer       |
| GET    | `/reviews/products/<product_id>/`           | List reviews for product          | None        |
| GET    | `/reviews/<id>/`                            | Review detail                     | Any         |
| PUT    | `/reviews/<id>/`                            | Update review                     | Owner/Admin |
| DELETE | `/reviews/<id>/`                            | Delete review                     | Owner/Admin |
| GET    | `/reviews/discussions/<product_id>/`        | List discussion threads           | Any (auth)  |
| POST   | `/reviews/discussions/<product_id>/`        | Create thread                     | Auth        |
| POST   | `/reviews/discussions/thread/<id>/reply/`   | Reply to thread                   | Auth        |

### 🏪 Seller

| Method | Endpoint                    | Description              | Auth   |
|--------|-----------------------------|--------------------------|--------|
| GET    | `/seller/dashboard/`        | Aggregated dashboard     | Seller |
| GET    | `/seller/products/`         | Own products list        | Seller |
| GET    | `/seller/profile/`          | View seller profile      | Seller |
| PUT    | `/seller/profile/`          | Update seller profile    | Seller |
| POST   | `/seller/profile/create/`   | Create seller profile    | Seller |

### 🛡️ Admin

| Method | Endpoint                          | Description                          | Auth  |
|--------|-----------------------------------|--------------------------------------|-------|
| GET    | `/admin/users/`                   | List all users                       | Admin |
| GET    | `/admin/users/<id>/`              | User detail                          | Admin |
| POST   | `/admin/users/<id>/suspend/`      | Suspend user                         | Admin |
| POST   | `/admin/users/<id>/activate/`     | Activate user                        | Admin |
| POST   | `/admin/sellers/<id>/verify/`     | Verify seller                        | Admin |
| GET    | `/admin/stats/`                   | Platform statistics                  | Admin |
| GET    | `/admin/orders/`                  | All orders                           | Admin |
| GET    | `/admin/analytics/`               | Full analytics dashboard             | Admin |
| GET    | `/admin/reported-content/`        | List unresolved content reports      | Admin |
| POST   | `/admin/assisted-upload/`         | Bulk upload on behalf of seller      | Admin |

### 💰 Pricing

| Method | Endpoint                            | Description              | Auth  |
|--------|-------------------------------------|--------------------------|-------|
| GET    | `/pricing/history/<product_id>/`    | Product price history    | Any   |
| GET    | `/pricing/alerts/`                  | List own alerts          | Buyer |
| POST   | `/pricing/alerts/`                  | Create price alert       | Buyer |
| DELETE | `/pricing/alerts/<id>/cancel/`      | Cancel alert             | Buyer |

### 🎟️ Promotions

| Method | Endpoint                          | Description                       | Auth   |
|--------|-----------------------------------|-----------------------------------|--------|
| GET    | `/promotions/coupons/`            | List own coupons                  | Seller |
| POST   | `/promotions/coupons/`            | Create a coupon                   | Seller |
| GET    | `/promotions/coupons/<id>/`       | Coupon detail                     | Seller |
| PUT    | `/promotions/coupons/<id>/`       | Update coupon                     | Seller |
| DELETE | `/promotions/coupons/<id>/`       | Delete coupon                     | Seller |
| GET    | `/promotions/promopricing/`       | List own promotional prices       | Seller |
| POST   | `/promotions/promopricing/`       | Create promotional price          | Seller |
| GET    | `/promotions/promopricing/<id>/`  | Promo pricing detail              | Seller |
| PUT    | `/promotions/promopricing/<id>/`  | Update promo pricing              | Seller |
| DELETE | `/promotions/promopricing/<id>/`  | Delete promo pricing              | Seller |

### 🔔 Notifications

| Method | Endpoint                           | Description                       | Auth |
|--------|------------------------------------|-----------------------------------|------|
| GET    | `/notifications/`                  | List notifications (`?unread=true` filter) | JWT  |
| POST   | `/notifications/read-all/`         | Mark all notifications as read    | JWT  |
| DELETE | `/notifications/clear/`            | Delete all notifications          | JWT  |
| POST   | `/notifications/<id>/read/`        | Mark single notification as read  | JWT  |
| DELETE | `/notifications/<id>/`             | Delete single notification        | JWT  |

**WebSocket:** `ws://<host>/ws/notifications/` — Connect with `Authorization: Bearer <token>` header. Receives real-time `order_update`, `price_drop`, and `promotion_alert` events.

### 💖 Wishlist

| Method | Endpoint             | Description                          | Auth  |
|--------|----------------------|--------------------------------------|-------|
| GET    | `/wishlist/`         | Get own wishlist with all items      | Buyer |
| POST   | `/wishlist/add/`     | Add product to wishlist (idempotent) | Buyer |
| DELETE | `/wishlist/remove/`  | Remove product from wishlist         | Buyer |
| DELETE | `/wishlist/clear/`   | Remove all items from wishlist       | Buyer |

### 🤖 AI Engine

| Method | Endpoint                        | Description                      | Auth |
|--------|---------------------------------|----------------------------------|------|
| GET    | `/ai/recommend/<product_id>/`   | AI-ranked buying recommendations | Any  |

---

## 🤖 AI Buying Tool — How It Works

The AI engine scores comparable products across 5 weighted factors:

| Factor         | Weight | Logic                                        |
|----------------|--------|----------------------------------------------|
| Price          | 40%    | Lower price → higher score (inverted norm)   |
| Seller Rating  | 25%    | Higher seller avg rating → higher score      |
| Review Score   | 10%    | Higher avg review stars → higher score       |
| Stock          | 15%    | More stock → higher score (capped at 100)    |
| Price Trend    | 10%    | Falling → 1.0, Stable → 0.5, Rising → 0.0   |

Returns a ranked list with composite AI score (0–1) and a human-readable explanation per option.

**Example Response:**
```json
{
  "status": "success",
  "best_recommendation": {
    "product_id": "uuid-...",
    "product_name": "Wireless Headphones",
    "price": "159.99",
    "ai_score": 0.8732,
    "explanation": "Excellent overall value. Competitively priced at $159.99. Highly rated seller (4.8/5). 📉 Price trend is falling — good time to buy. Customer reviews avg 4.6/5 stars."
  },
  "ranked_options": [...]
}
```

---

## 📦 Bulk Product Upload

**Endpoint:** `POST /api/v1/products/bulk-upload/`  
**Format:** `multipart/form-data`, field name: `file`  
**Accepted:** `.xlsx` files only

**Required columns in Excel:**

| Column      | Type    | Notes                          |
|-------------|---------|--------------------------------|
| name        | string  | Product name                   |
| description | string  | Optional, can be blank         |
| price       | decimal | Must be ≥ 0                    |
| stock_qty   | integer | Must be ≥ 0                    |
| SKU         | string  | Must be globally unique        |
| category    | string  | Auto-created if not exists     |

**Response includes:**
- `created_count` — rows successfully imported
- `error_count` — rows that failed
- `errors[]` — per-row error details with row number

Admins can also upload on behalf of a seller using `POST /api/v1/admin/assisted-upload/` with an additional `seller_id` field.

---

## 🔐 Security Implementation

| Feature                 | Implementation                              |
|-------------------------|---------------------------------------------|
| Password Hashing        | BCryptSHA256PasswordHasher (default)        |
| JWT Tokens              | Access (60min) + Refresh (7d) + Blacklist   |
| 2FA                     | TOTP via pyotp (Google Authenticator compatible) |
| Input Validation        | DRF serializer-level validation             |
| SQL Injection           | Django ORM (parameterized queries always)   |
| XSS Protection          | `SECURE_BROWSER_XSS_FILTER = True`          |
| CSRF Protection         | `CsrfViewMiddleware` enabled                |
| Clickjacking            | `X_FRAME_OPTIONS = 'DENY'`                  |
| Content Sniffing        | `SECURE_CONTENT_TYPE_NOSNIFF = True`        |
| HSTS                    | Enabled in production (31536000s)           |
| Rate Limiting           | 100/hr anon, 1000/hr authenticated          |
| RBAC                    | Permission classes per role on every view   |
| Stripe Webhooks         | Signature verified with `STRIPE_WEBHOOK_SECRET` |

---

## 🧪 Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=. --cov-report=html

# Run specific module
pytest tests/test_orders.py -v

# Run only fast tests (exclude slow)
pytest -m "not slow"
```

**Test coverage targets:**
- `tests/test_users.py` — User model + auth endpoints (9 test cases)
- `tests/test_products.py` — Product model + API (11 test cases)
- `tests/test_cart.py` — Cart model + API (11 test cases)
- `tests/test_orders.py` — Order model + checkout + transitions (12 test cases)
- `tests/test_reviews.py` — Review model + API (6 test cases)
- `tests/test_admin_panel.py` — Admin RBAC + management (10 test cases)
- `tests/test_ai_engine.py` — AI scoring engine + recommend API (9 test cases)
- `tests/test_sellers.py` — Seller profile + dashboard (10 test cases)
- `tests/test_pricing.py` — Price history + alerts + Celery task (12 test cases)
- `tests/test_wishlists.py` — Wishlist model + API (8 test cases)
- `tests/test_notifications.py` — Notification REST API (8 test cases)

---

## ⚙️ Celery Tasks

| Task                                    | Schedule          | Description                                    |
|-----------------------------------------|-------------------|------------------------------------------------|
| `pricing.check_price_alerts`            | Every 30 minutes  | Scan price alerts; trigger + email buyers      |
| `admin_panel.generate_daily_report`     | Daily midnight    | Log platform metrics (users, orders, revenue)  |
| `products.check_price_freshness`        | Daily at 01:00    | Notify sellers of stale products (>30 days)    |

Start workers:
```bash
# Worker
celery -A core worker --loglevel=info

# Beat scheduler
celery -A core beat --loglevel=info

# Monitor with Flower
celery -A core flower
```

---

## 🗃️ Database Schema Summary

| Model              | Key Fields                                                          |
|--------------------|---------------------------------------------------------------------|
| `User`             | UUID PK, email, name, phone, role, verified, is_active, is_2fa_enabled |
| `SellerProfile`    | user (1-1), business_name, rating_avg, verified, commission         |
| `Category`         | name, slug, parent (self-FK)                                        |
| `Product`          | seller, category, name, price, stock_qty, SKU, views_count, clicks_count |
| `ProductImage`     | product, image, alt_text, is_primary                                |
| `Collection`       | seller, name, slug, products (M2M), is_active                      |
| `PriceHistory`     | product, price, recorded_at (auto on product save)                  |
| `PriceAlert`       | buyer, product, target_price, status, triggered_at                  |
| `Cart`             | buyer (1-1)                                                         |
| `CartItem`         | cart, product, quantity, price_at_add                               |
| `Order`            | buyer, total_amount, status, payment_ref, coupon_applied, shipping_address |
| `OrderItem`        | order, product, quantity, unit_price, subtotal (auto)               |
| `Review`           | product, buyer, stars (1-5), comment (unique per buyer+prod)        |
| `DiscussionThread` | product, user, title, body, is_resolved                             |
| `DiscussionReply`  | thread, user, body                                                  |
| `Coupon`           | code, discount_type, discount_amount, seller_restricted, validity    |
| `PromoPricing`     | product (1-1), promo_price, start_date, end_date, is_active         |
| `Notification`     | recipient, title, message, notification_type, related_entity, is_read |
| `Wishlist`         | buyer (1-1)                                                         |
| `WishlistItem`     | wishlist, product, added_at                                         |

---

## 📋 Django Admin Panel

All models are registered with full admin support. Access at `/django-admin/`.

**Actions available:**
- Users → Suspend / Activate / Verify
- Sellers → Verify / Unverify
- Products → Activate / Deactivate
- Orders → View with inline items
- Notifications → Mark selected as read
- Wishlists → View with inline items

---

## 📁 Project Structure

```
backend/
├── core/
│   ├── settings.py          # All Django settings (env-driven)
│   ├── urls.py              # Root URL dispatcher
│   ├── asgi.py              # ASGI app (HTTP + WebSocket via Daphne)
│   ├── celery.py            # Celery app + beat schedule
│   ├── pagination.py        # StandardResultsPagination
│   ├── permissions.py       # IsBuyer, IsSeller, IsAdmin, IsOwnerOrAdmin…
│   ├── exceptions.py        # Unified JSON error responses
│   ├── middleware.py        # Request logging
│   └── websocket_auth.py   # JWT middleware for WebSocket connections
├── api/
│   └── urls.py              # Central /api/v1/ router
├── users/                   # Auth: register, login, logout, profile, 2FA, Google OAuth
├── sellers/                 # SellerProfile CRUD + dashboard + analytics
├── products/                # Products, categories, collections, compare, bulk upload
├── pricing/                 # PriceHistory, PriceAlert, Celery tasks
├── cart/                    # Cart management
├── orders/                  # Checkout (atomic), order lifecycle, Stripe, EasyPost
├── reviews/                 # Reviews + discussion threads + content reports
├── admin_panel/             # Admin controls, analytics, assisted upload
├── ai_engine/               # Scoring engine + recommendation API
├── promotions/              # Coupons + promotional pricing
├── notifications/           # In-app notifications (REST) + WebSocket consumer
├── wishlists/               # Buyer wishlist (add/remove/clear)
├── tests/                   # Full pytest test suite (conftest + 11 modules)
├── manage.py
├── requirements.txt
├── pytest.ini
├── Dockerfile               # Multi-stage production build
├── docker-compose.yml       # Full-stack local/prod composition
├── nginx.conf               # Nginx reverse proxy
└── .env.example             # Environment variable template
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Write tests for your changes
4. Ensure all tests pass (`pytest`)
5. Submit a pull request

---

## 📄 License

MIT License — see `LICENSE` for details.
