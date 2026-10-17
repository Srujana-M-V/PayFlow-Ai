from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from payment_project.authentication import GatewayUser
from transactions.models import Transaction
from transactions.views import TransactionListView


class TransactionTenantIsolationTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

        Transaction.objects.create(
            organization_id="e70ea7a1-6322-4ff9-b8f3-254f71785ca5",
            order_id="TENANT1-AUTO-TEST",
            amount="100.00",
            currency="INR",
            status="INITIATED",
        )

        Transaction.objects.create(
            organization_id="06e1ee70-f2ba-4049-8667-34582aac8bd7",
            order_id="TENANT5-AUTO-TEST",
            amount="200.00",
            currency="INR",
            status="INITIATED",
        )

    def test_user_sees_only_own_organization_transactions(self):
        request = self.factory.get("/api/transactions/")
        force_authenticate(
            request,
            user=GatewayUser(
                user_id=3,
                organization_id="06e1ee70-f2ba-4049-8667-34582aac8bd7",
                role="MERCHANT_ADMIN",
            ),
        )

        response = TransactionListView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]["order_id"],
            "TENANT5-AUTO-TEST",
        )