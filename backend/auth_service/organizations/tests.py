
from django.test import TestCase
from rest_framework.test import APIClient

from organizations.models import Organization
from users.models import User


class TenantIsolationTests(TestCase):
    def setUp(self):
        self.org1 = Organization.objects.create(
            name="Merchant One",
            slug="merchant-one",
        )
        self.org2 = Organization.objects.create(
            name="Merchant Two",
            slug="merchant-two",
        )

        self.merchant = User.objects.create_user(
            username="merchant1",
            password="TestPass123!",
            organization=self.org1,
            role=User.Role.MERCHANT_ADMIN,
        )

        self.super_admin = User.objects.create_user(
            username="superadmin",
            password="TestPass123!",
            role=User.Role.SUPER_ADMIN,
        )

        self.client = APIClient()

    def test_merchant_cannot_access_other_organization(self):
        self.client.force_authenticate(user=self.merchant)

        response = self.client.get(
            f"/api/organizations/merchants/{self.org2.id}/"
        )

        self.assertEqual(response.status_code, 404)

    def test_merchant_can_access_own_organization(self):
        self.client.force_authenticate(user=self.merchant)

        response = self.client.get(
            f"/api/organizations/merchants/{self.org1.id}/"
        )

        self.assertEqual(response.status_code, 200)

    def test_super_admin_can_access_other_organization(self):
        self.client.force_authenticate(user=self.super_admin)

        response = self.client.get(
            f"/api/organizations/merchants/{self.org2.id}/"
        )

        self.assertEqual(response.status_code, 200)

    def test_merchant_cannot_create_organization(self):
        self.client.force_authenticate(user=self.merchant)

        response = self.client.post(
            "/api/organizations/create/",
            {
                "name": "Unauthorized Merchant",
                "slug": "unauthorized-merchant",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(
            Organization.objects.filter(
                slug="unauthorized-merchant"
            ).exists()
        )

    def test_super_admin_can_create_organization(self):
        self.client.force_authenticate(user=self.super_admin)

        response = self.client.post(
            "/api/organizations/create/",
            {
                "name": "New Merchant",
                "slug": "new-merchant",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            Organization.objects.filter(slug="new-merchant").exists()
        )
    def test_merchant_can_list_only_own_organization(self):
        self.client.force_authenticate(user=self.merchant)

        response = self.client.get("/api/organizations/merchants/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.org1.id)

    def test_super_admin_can_list_all_organizations(self):
        self.client.force_authenticate(user=self.super_admin)

        response = self.client.get("/api/organizations/merchants/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)