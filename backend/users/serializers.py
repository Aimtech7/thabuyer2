"""users/serializers.py"""
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('name', 'email', 'phone', 'role', 'password', 'password_confirm')
        extra_kwargs = {
            'role': {'default': 'buyer'},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        # Prevent self-assigning admin role
        if attrs.get('role') == 'admin':
            raise serializers.ValidationError({'role': 'Cannot self-register as admin.'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(
            request=self.context.get('request'),
            username=attrs['email'],
            password=attrs['password'],
        )
        if not user:
            raise serializers.ValidationError('Invalid credentials.')
        if not user.is_active:
            raise serializers.ValidationError('This account has been suspended.')
        attrs['user'] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name', 'email', 'phone', 'role', 'verified', 'date_joined', 'is_2fa_enabled')
        read_only_fields = ('id', 'role', 'verified', 'date_joined', 'is_2fa_enabled')


class UserAdminSerializer(serializers.ModelSerializer):
    """Full serializer for admin operations."""

    class Meta:
        model = User
        fields = (
            'id', 'name', 'email', 'phone', 'role',
            'verified', 'is_active', 'date_joined', 'last_login', 'is_2fa_enabled'
        )
        read_only_fields = ('id', 'date_joined', 'last_login')


class TokenResponseSerializer(serializers.Serializer):
    """Response shape for login/register."""
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserSerializer()

class TwoFactorSetupSerializer(serializers.Serializer):
    secret = serializers.CharField()
    provisioning_uri = serializers.CharField()

class TwoFactorVerifySerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6)

class TwoFactorLoginVerifySerializer(serializers.Serializer):
    temp_token = serializers.CharField()
    otp = serializers.CharField(max_length=6)
