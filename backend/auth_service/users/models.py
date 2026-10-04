from django.contrib.auth.models import AbstractUser
from django.db import models
from organizations.models import Organization


class User(AbstractUser):
    class Role(models.TextChoices):
        SUPER_ADMIN = "SUPER_ADMIN", "Super Admin"
        MERCHANT_ADMIN = "MERCHANT_ADMIN", "Merchant Admin"
        ACCOUNTANT = "ACCOUNTANT", "Accountant"
        SUPPORT = "SUPPORT", "Support"
        FRAUD_ANALYST = "FRAUD_ANALYST", "Fraud Analyst"

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="users",
        null=True,
        blank=True,
    )
    role = models.CharField(
        max_length=30,
        choices=Role.choices,
        default=Role.MERCHANT_ADMIN,
    )

    def __str__(self):
        return self.username