"""users/urls.py"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, LoginView, LogoutView, ProfileView, GoogleLogin,
    Setup2FAView, Verify2FASetupView, Verify2FALoginView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth-register'),
    path('login/', LoginView.as_view(), name='auth-login'),
    path('logout/', LogoutView.as_view(), name='auth-logout'),
    path('google/', GoogleLogin.as_view(), name='google-login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('profile/', ProfileView.as_view(), name='user-profile'),
    path('2fa/setup/', Setup2FAView.as_view(), name='2fa-setup'),
    path('2fa/verify-setup/', Verify2FASetupView.as_view(), name='2fa-verify-setup'),
    path('2fa/verify-login/', Verify2FALoginView.as_view(), name='2fa-verify-login'),
]
