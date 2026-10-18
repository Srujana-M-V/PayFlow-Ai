from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("users.urls")),
    path("api/organizations/", include("organizations.urls")),
    path("o/", include("oauth2_provider.urls", namespace="oauth2_provider")),
]