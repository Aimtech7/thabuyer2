"""users/views.py"""
from rest_framework import status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .models import User
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
)


class RegisterView(APIView):
    """Register a new user (Buyer or Seller)."""
    permission_classes = [AllowAny]

    @extend_schema(
        request=RegisterSerializer,
        responses={201: OpenApiResponse(description='User registered successfully')},
        tags=['Authentication'],
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                'status': 'success',
                'message': 'Registration successful.',
                'data': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'user': UserSerializer(user).data,
                },
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """Authenticate and receive JWT tokens."""
    permission_classes = [AllowAny]

    @extend_schema(
        request=LoginSerializer,
        responses={200: OpenApiResponse(description='Login successful')},
        tags=['Authentication'],
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        if user.is_2fa_enabled:
            from django.core.signing import TimestampSigner
            signer = TimestampSigner()
            temp_token = signer.sign(str(user.id))
            return Response(
                {
                    'status': 'requires_2fa',
                    'message': '2FA is enabled. Please provide your OTP.',
                    'temp_token': temp_token
                },
                status=status.HTTP_200_OK
            )

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                'status': 'success',
                'message': 'Login successful.',
                'data': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'user': UserSerializer(user).data,
                },
            },
            status=status.HTTP_200_OK,
        )


import pyotp

class Setup2FAView(APIView):
    """Generate a TOTP secret and provisioning URI."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if user.is_2fa_enabled:
            return Response({'error': '2FA is already enabled.'}, status=status.HTTP_400_BAD_REQUEST)
        
        secret = pyotp.random_base32()
        user.totp_secret = secret
        user.save()
        
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(name=user.email, issuer_name="THABUYER")
        
        return Response({
            'secret': secret,
            'provisioning_uri': provisioning_uri
        })


class Verify2FASetupView(APIView):
    """Verify the first OTP to enable 2FA."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        otp = request.data.get('otp')
        if not otp:
            return Response({'error': 'OTP is required.'}, status=status.HTTP_400_BAD_REQUEST)
            
        if user.is_2fa_enabled:
            return Response({'error': '2FA is already enabled.'}, status=status.HTTP_400_BAD_REQUEST)
            
        if not user.totp_secret:
            return Response({'error': 'TOTP secret not generated. Call setup first.'}, status=status.HTTP_400_BAD_REQUEST)
            
        totp = pyotp.TOTP(user.totp_secret)
        if totp.verify(otp):
            user.is_2fa_enabled = True
            user.save()
            return Response({'status': 'success', 'message': '2FA enabled successfully.'})
        return Response({'error': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)


class Verify2FALoginView(APIView):
    """Verify OTP and temp_token during login to issue JWT."""
    permission_classes = [AllowAny]

    def post(self, request):
        temp_token = request.data.get('temp_token')
        otp = request.data.get('otp')
        if not temp_token or not otp:
            return Response({'error': 'temp_token and otp are required.'}, status=status.HTTP_400_BAD_REQUEST)
            
        from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
        signer = TimestampSigner()
        try:
            # Valid for 5 minutes (300 seconds)
            user_id = signer.unsign(temp_token, max_age=300)
        except SignatureExpired:
            return Response({'error': 'Token expired.'}, status=status.HTTP_400_BAD_REQUEST)
        except BadSignature:
            return Response({'error': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_400_BAD_REQUEST)
            
        if not user.is_2fa_enabled or not user.totp_secret:
            return Response({'error': '2FA is not enabled for this user.'}, status=status.HTTP_400_BAD_REQUEST)
            
        totp = pyotp.TOTP(user.totp_secret)
        if totp.verify(otp):
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    'status': 'success',
                    'message': 'Login successful.',
                    'data': {
                        'access': str(refresh.access_token),
                        'refresh': str(refresh),
                        'user': UserSerializer(user).data,
                    },
                },
                status=status.HTTP_200_OK,
            )
            
        return Response({'error': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """Blacklist the refresh token on logout."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'status': 'success', 'message': 'Logged out.'})
        except Exception:
            return Response(
                {'status': 'error', 'message': 'Invalid token.'},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ProfileView(generics.RetrieveUpdateAPIView):
    """Get or update authenticated user's profile."""
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class GoogleLogin(SocialLoginView):
    """
    Callback/Endpoint for Google OAuth frontend exchange.
    Requires an access_token or code passed from the frontend.
    """
    adapter_class = GoogleOAuth2Adapter
    callback_url = "http://localhost:3000/auth/google/callback" # Update for frontend URL
    client_class = OAuth2Client
