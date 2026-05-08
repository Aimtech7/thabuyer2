# README Audit — Gap Analysis

A comparison of every feature/endpoint documented in `README.MD` against what is actually implemented in the codebase, plus features in code that are **not mentioned** in the README.

---

## ✅ FULLY IMPLEMENTED (README is accurate)

| Area | Claim | Verdict |
|---|---|---|
| Auth — register, login, logout, token-refresh, profile | All 6 endpoints exist | ✅ |
| Products — list, create, detail, update, compare, search, bulk-upload, categories | All 8 endpoints exist | ✅ |
| Cart — view, add, remove, clear | All 4 endpoints exist | ✅ |
| Orders — checkout, list, detail, status-update | All 4 endpoints exist | ✅ |
| Reviews — create, list-by-product, detail, update, delete | All 5 endpoints exist | ✅ |
| Reviews — discussions list/create, reply | All 3 thread endpoints exist | ✅ |
| Seller — dashboard, own-products, profile GET/PUT/create | All 5 endpoints exist | ✅ |
| Admin — user list/detail, suspend, activate, verify-seller, stats, orders | All 7 endpoints exist | ✅ |
| Pricing — price history, list alerts, create alert, cancel alert | All 4 endpoints exist | ✅ |
| AI Engine — `GET /ai/recommend/<product_id>/` | Endpoint exists | ✅ |
| Celery — `pricing.check_price_alerts` every 30 min | Configured in `core/celery.py` | ✅ |
| Celery — `admin_panel.generate_daily_report` daily at midnight | Configured in `core/celery.py` | ✅ |
| Security — BCrypt, JWT, rate-limiting, CORS, HSTS, XSS, CSRF, clickjacking | All settings present | ✅ |
| Docker — Dockerfile, docker-compose.yml, nginx.conf | All files exist | ✅ |
| API Docs — `/api/docs/` (Swagger) via drf-spectacular | Configured and routed | ✅ |
| WebSocket — ASGI + Channels + JWT auth middleware | `core/asgi.py` wired correctly | ✅ |
| Test suite — 7 test modules (users, products, cart, orders, reviews, admin, ai_engine) | All 7 files exist in `tests/` | ✅ |

---

## ❌ NOT IMPLEMENTED / MISSING FROM README

### 1. `wishlists` App — Empty Shell
- **`backend/wishlists/`** contains only an `__init__.py` with a comment.
- **No model, no views, no serializer, no URLs, not registered in `INSTALLED_APPS`.**
- **Action:** Build out full Wishlist CRUD.

---

### 2. `notifications` App — Missing REST API Endpoints
- The `Notification` model and WebSocket `NotificationConsumer` exist.
- **But:** There are **no HTTP REST endpoints** (`/notifications/`) to list, mark-as-read, or clear notifications.
- The app is **not wired into `api/urls.py`**.
- **Action:** Add serializer, views, URLs, register in `api/urls.py`.

---

### 3. `notifications` App — Missing `apps.py` / `migrations`
- Missing a formal `apps.py` and initial migration file.
- **Action:** Create `apps.py` and run `makemigrations notifications`.

---

### 4. README Celery Section Incomplete
- README documents only **2 periodic tasks** but `core/celery.py` schedules **3**:
  - `pricing.check_price_alerts` ✅ documented
  - `admin_panel.generate_daily_report` ✅ documented
  - **`products.tasks.check_price_freshness`** ❌ **NOT in README** (runs daily at 01:00)

---

### 5. README API Reference — 16 Missing Endpoints

| Method | Endpoint | What it does |
|---|---|---|
| GET | `/products/<id>/click/` | Increment click count for analytics |
| GET/POST | `/products/collections/` | Seller product collections |
| GET/PUT/DELETE | `/products/collections/<id>/` | Manage a specific collection |
| GET/POST | `/promotions/coupons/` | Seller coupon management |
| GET/PUT/DELETE | `/promotions/coupons/<id>/` | Manage specific coupon |
| GET/POST | `/promotions/promopricing/` | Promotional pricing |
| GET/PUT/DELETE | `/promotions/promopricing/<id>/` | Manage specific promo price |
| POST | `/auth/google/` | Google OAuth login |
| POST | `/auth/2fa/setup/` | Generate TOTP secret |
| POST | `/auth/2fa/verify-setup/` | Confirm + enable 2FA |
| POST | `/auth/2fa/verify-login/` | OTP verification during login |
| POST | `/orders/webhook/stripe/` | Stripe payment webhook |
| POST | `/orders/<id>/fulfill/` | Generate shipping label (EasyPost) |
| GET | `/admin/analytics/` | Full admin analytics dashboard |
| GET | `/admin/reported-content/` | List unresolved content reports |
| POST | `/admin/assisted-upload/` | Admin bulk upload on behalf of seller |

---

### 6. README Database Schema — 4 Missing Models

| Model | App | In README Schema? |
|---|---|---|
| `Collection` | products | ❌ Missing |
| `Notification` | notifications | ❌ Missing |
| `Coupon` | promotions | ❌ Missing |
| `PromoPricing` | promotions | ❌ Missing |

---

### 7. README Tech Stack — 8 Missing Technologies

| Tech | Used In |
|---|---|
| Django Channels + Daphne | WebSocket real-time notifications |
| django-allauth | Google OAuth + social login |
| dj-rest-auth | Social login integration |
| Stripe | Payment processing in checkout |
| EasyPost | Shipping label generation |
| pyotp | TOTP-based 2FA |
| whitenoise | Static file serving |
| channels-redis | Redis channel layer for WebSockets |

---

### 8. README Tests — 2 Missing Test Files

| Test File | In README? |
|---|---|
| `test_sellers.py` | ❌ Not mentioned |
| `test_pricing.py` | ❌ Not mentioned |

---

### 9. README Architecture — 3 Missing Apps

README diagram does not include:
- `notifications`
- `promotions`
- `wishlists`

---

## 📋 Implementation Priority

| Priority | Item | Action |
|---|---|---|
| 🔴 High | `wishlists` app | Build full model, serializer, views, URLs, admin, migration |
| 🔴 High | `notifications` REST endpoints | Add serializer, views, URLs; wire into `api/urls.py` |
| 🔴 High | `notifications` admin.py | Register `Notification` model |
| 🟡 Medium | README — API Reference | Add all 16 missing endpoints |
| 🟡 Medium | README — Celery section | Add `products.tasks.check_price_freshness` |
| 🟡 Medium | README — Schema section | Add 4 missing models |
| 🟡 Medium | README — Tech Stack | Add 8 missing technologies |
| 🟢 Low | README — Tests section | Add `test_sellers.py` and `test_pricing.py` |
| 🟢 Low | README — Architecture | Add `notifications`, `promotions`, `wishlists` to tree |
