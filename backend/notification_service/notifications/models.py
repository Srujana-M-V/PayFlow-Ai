import uuid

from django.db import models


class Notification(models.Model):

    class NotificationType(models.TextChoices):
        PAYMENT_SUCCESS = "PAYMENT_SUCCESS", "Payment Success"
        PAYMENT_FAILED = "PAYMENT_FAILED", "Payment Failed"
        REFUND = "REFUND", "Refund"
        FRAUD_ALERT = "FRAUD_ALERT", "Fraud Alert"
        GATEWAY_HEALTH = "GATEWAY_HEALTH", "Gateway Health"
        RECONCILIATION = "RECONCILIATION", "Reconciliation"
        INVESTIGATION = "INVESTIGATION", "Investigation"

    class Channel(models.TextChoices):
        EMAIL = "EMAIL", "Email"
        SMS = "SMS", "SMS"
        IN_APP = "IN_APP", "In App"
        WEBHOOK = "WEBHOOK", "Webhook"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PROCESSING = "PROCESSING", "Processing"
        SENT = "SENT", "Sent"
        FAILED = "FAILED", "Failed"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    organization_id = models.UUIDField()
    user_id = models.UUIDField(null=True, blank=True)

    transaction_id = models.UUIDField(
        null=True,
        blank=True,
    )

    event_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    notification_type = models.CharField(
        max_length=50,
        choices=NotificationType.choices,
    )

    channel = models.CharField(
        max_length=20,
        choices=Channel.choices,
    )

    recipient_email = models.EmailField(
        max_length=255,
        null=True,
        blank=True,
    )

    recipient_phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
    )

    subject = models.CharField(max_length=255)
    message = models.TextField()

    payload = models.JSONField(
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    retry_count = models.PositiveIntegerField(default=0)
    max_retries = models.PositiveIntegerField(default=3)

    error_message = models.TextField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["organization_id"]),
            models.Index(fields=["transaction_id"]),
            models.Index(fields=["notification_type"]),
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.notification_type} - {self.status}"
