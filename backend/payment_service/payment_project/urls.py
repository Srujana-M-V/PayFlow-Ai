from django.contrib import admin
from django.urls import path

from transactions.views import TransactionListView

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "api/transactions/",
        TransactionListView.as_view(),
        name="transaction-list",
    ),
]