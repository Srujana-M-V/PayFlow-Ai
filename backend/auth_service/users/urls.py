from django.urls import path

from .views import (
    LoginView,
    LogoutView,
    OAuthBrowserLoginView,
    ProtectedView,
    RefreshTokenView,
    RegistrationView,
)

urlpatterns = [
    path("register/", RegistrationView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("browser-login/", OAuthBrowserLoginView.as_view(), name="browser-login"),
    path("refresh/", RefreshTokenView.as_view(), name="refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("protected/", ProtectedView.as_view(), name="protected"),
]