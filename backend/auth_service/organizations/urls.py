from django.urls import path

from .merchant_views import MerchantDetailView, MerchantListCreateView
from .views import OrganizationCreateView

urlpatterns = [
    path("create/", OrganizationCreateView.as_view(), name="organization-create"),
    path("merchants/", MerchantListCreateView.as_view(), name="merchant-list-create"),
    path(
        "merchants/<int:organization_id>/",
        MerchantDetailView.as_view(),
        name="merchant-detail",
    ),
]