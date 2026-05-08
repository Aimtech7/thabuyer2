# Module 1: Authentication & Onboarding Implementation Plan

This plan covers the implementation of the first phase of the SRS v2.0 missing features, focusing on Two-Factor Authentication (2FA), Seller Commission Policy agreement, and the Assisted Upload Service for admins.

## Proposed Changes

### Backend Dependencies
#### [MODIFY] backend/requirements.txt
- Add `pyotp` and `qrcode` to the dependencies.

### Users App (2FA)

#### [MODIFY] backend/users/models.py
- Add `totp_secret` (CharField, null=True, blank=True) and `is_2fa_enabled` (BooleanField, default=False) to the `User` model.

#### [MODIFY] backend/users/serializers.py
- Add `TwoFactorSetupSerializer` and `TwoFactorVerifySerializer`.

#### [MODIFY] backend/users/views.py
- Update `LoginView`: If `user.is_2fa_enabled` is True, generate a temporary signed token (using `django.core.signing.TimestampSigner`) valid for 5 minutes, and return `{"status": "requires_2fa", "temp_token": "..."}` instead of standard JWTs.
- Create `Setup2FAView`: Generates a base32 `totp_secret`, saves it, and returns the `otpauth://` provisioning URI.
- Create `Verify2FASetupView`: Validates the first OTP code and sets `is_2fa_enabled = True`.
- Create `Verify2FALoginView`: Validates the `temp_token` and the OTP code, then issues the final JWT access and refresh tokens.

#### [MODIFY] backend/users/urls.py
- Add endpoints: `/api/users/2fa/setup/`, `/api/users/2fa/verify-setup/`, and `/api/users/2fa/verify-login/`.

### Sellers App (Commission Policy)

#### [MODIFY] backend/sellers/models.py
- Add `commission_accepted` (BooleanField, default=False) and `commission_accepted_at` (DateTimeField, null=True) to `SellerProfile`.

#### [MODIFY] backend/sellers/serializers.py
- Update `SellerProfileCreateSerializer` to require `commission_accepted`. If false, raise a validation error. If true, set `commission_accepted_at` to the current time.

### Admin Panel (Assisted Upload Service)

#### [NEW] backend/admin_panel/views.py
- Implement an `AdminAssistedUploadView` that allows Admins to upload an `.xlsx` file on behalf of a specific seller. It will reuse the Excel parsing logic but override the owner ID.

#### [MODIFY] backend/admin_panel/urls.py
- Register the new `AdminAssistedUploadView` endpoint.
