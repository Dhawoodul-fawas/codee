from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.generics import ListAPIView
from django.contrib.auth.models import User

from .serializers import LoginSerializer, RegisterSerializer, UserListSerializer
from .utils import api_response   # ✅ IMPORTANT


# ✅ REGISTER API
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return api_response(
                success=True,
                message="User created successfully!",
                data=serializer.data,
                status_code=status.HTTP_201_CREATED
            )

        return api_response(
            success=False,
            message="User registration failed",
            data=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )


# ✅ LOGIN API
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            return api_response(
                success=True,
                message="Login successful!",
                data=serializer.validated_data,
                status_code=status.HTTP_200_OK
            )

        return api_response(
            success=False,
            message="Invalid login credentials",
            data=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )


# ✅ USER LIST API
class RegisterListView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)

        return api_response(
            success=True,
            message="User list fetched successfully",
            data=response.data
        )
