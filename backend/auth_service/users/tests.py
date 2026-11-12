from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from organizations.models import Organization
from users.models import User


class AuthenticationTests(TestCase):

    def setUp(self):
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-organization",
        )

        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="TestPassword@123",
            organization=self.organization,
            role=User.Role.MERCHANT_ADMIN,
        )

        self.client = APIClient()

    def test_user_registration(self):
        response = self.client.post(
            "/api/auth/register/",
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "NewPassword@123",
                "first_name": "New",
                "last_name": "User",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_login(self):
        response = self.client.post(
            "/api/auth/login/",
            {
                "username": "testuser",
                "password": "TestPassword@123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.data)
        self.assertIn("refresh_token", response.data)

    def test_invalid_login(self):
        response = self.client.post(
            "/api/auth/login/",
            {
                "username": "testuser",
                "password": "WrongPassword",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_protected_endpoint_without_token(self):
        response = self.client.get("/api/auth/protected/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_protected_endpoint_with_token(self):
        response = self.client.post(
            "/api/auth/login/",
            {
                "username": "testuser",
                "password": "TestPassword@123",
            },
            format="json",
        )

        access_token = response.data["access_token"]

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )

        response = self.client.get("/api/auth/protected/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["authentication_method"], "JWT")