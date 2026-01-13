from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
import re

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'password']


    def validate_email(self, value):
        pattern = r'^[a-zA-Z0-9._%+-]+@gmail\.com$'
        if not re.match(pattern, value):
            raise serializers.ValidationError("Only gmail.com email is allowed.")

        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email already exists.")

        return value
    
    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")

        if not re.search(r"[A-Z]", value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")

        if not re.search(r"[a-z]", value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter.")

        if not re.search(r"[0-9]", value):
            raise serializers.ValidationError("Password must contain at least one number.")

        if not re.search(r"[!@#$%^&*()_+=\-{}\[\]:;\"'<>,.?/]", value):
            raise serializers.ValidationError("Password must contain at least one special character.")

        return value


    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        # ✅ Gmail-only validation
        pattern = r'^[a-zA-Z0-9._%+-]+@gmail\.com$'
        if not re.match(pattern, email):
            raise serializers.ValidationError("Only gmail.com email is allowed.")

        # ✅ Strong password basic check (not 6-digit)
        if len(password) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")

        user = User.objects.filter(email=email).first()

        if user is None or not user.check_password(password):
            raise serializers.ValidationError("Invalid email or password.")

        refresh = RefreshToken.for_user(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            }
        }


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
