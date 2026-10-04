import uuid

from django.db import models


class Transaction(models.Model):
    class Status(models.TextChoices):
        INITIATED = "INITIATED", "Initiated"
        PROCESSING = "PROCESSING", "Processing"
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"
        REFUNDED = "REFUNDED", "Refunded"
        CHARGEBACK = "CHARGEBACK", "Chargeback"

    class FraudAction(models.TextChoices):
        ALLOWED = "ALLOWED", "Allowed"
        FLAGGED = "FLAGGED", "Flagged"
        BLOCKED = "BLOCKED", "Blocked"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization_id = models.UUIDField()
    order_id = models.CharField(max_length=255, unique=True)
    idempotency_key = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="INR")
    status = models.CharField(
        max_length=50,
        choices=Status.choices,
        default=Status.INITIATED,
    )
    gateway_used = models.CharField(max_length=50, null=True, blank=True)
    gateway_txn_id = models.CharField(max_length=255, null=True, blank=True)
    gateway_response = models.JSONField(null=True, blank=True)
    fraud_score = models.FloatField(null=True, blank=True)
    fraud_action = models.CharField(
        max_length=20,
        choices=FraudAction.choices,
        null=True,
        blank=True,
    )
    customer_email = models.EmailField(max_length=255, null=True, blank=True)
    customer_phone = models.CharField(max_length=20, null=True, blank=True)
    customer_ip = models.GenericIPAddressField(null=True, blank=True)
    device_fingerprint = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    initiated_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.order_id
