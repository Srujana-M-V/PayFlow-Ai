from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_protect

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from .serializers import LoginSerializer, RegistrationSerializer


class RegistrationView(APIView):
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "message": "User registered successfully",
                    "user_id": user.id,
                    "username": user.username,
                    "email": user.email,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data["user"]

            refresh_token = RefreshToken.for_user(user)
            refresh_token["organization_id"] = (
                str(user.organization.organization_uuid)
                if user.organization_id
                else None
            )
            refresh_token["role"] = user.role

            access_token = refresh_token.access_token

            return Response(
                {
                    "message": "Login successful",
                    "access_token": str(access_token),
                    "refresh_token": str(refresh_token),
                    "user_id": user.id,
                    "username": user.username,
                    "email": user.email,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class RefreshTokenView(TokenRefreshView):
    pass


class LogoutView(APIView):
    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {"error": "Refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {"message": "Logout successful."},
                status=status.HTTP_200_OK,
            )

        except Exception:
            return Response(
                {"error": "Invalid or expired refresh token."},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        authenticator = request.successful_authenticator
        module = (
            authenticator.__class__.__module__
            if authenticator
            else ""
        )

        if module.startswith("oauth2_provider"):
            authentication_method = "OAuth2"
        elif module.startswith("rest_framework_simplejwt"):
            authentication_method = "JWT"
        else:
            authentication_method = "Session"

        return Response(
            {
                "message": "Authentication successful.",
                "authentication_method": authentication_method,
                "user_id": request.user.id,
                "username": request.user.username,
            },
            status=status.HTTP_200_OK,
        )


class OAuthBrowserLoginView(View):
    template_name = "users/oauth_login.html"

    @method_decorator(csrf_protect)
    def get(self, request):
        return render(request, self.template_name)

    @method_decorator(csrf_protect)
    def post(self, request):
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is None or not user.is_active:
            return render(
                request,
                self.template_name,
                {"error": "Invalid username or password."},
                status=400,
            )

        login(request, user)
        next_url = request.GET.get("next") or request.POST.get("next")

        if next_url and next_url.startswith("/") and not next_url.startswith("//"):
            return redirect(next_url)

        return redirect("/api/auth/protected/")