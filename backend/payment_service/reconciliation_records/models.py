import uuid

from django.db import models


class ReconciliationRecord(models.Model):
    class Status(models.TextChoices):
        MATCHED = "MATCHED", "Matched"
        MISMATCH = "MISMATCH", "Mismatch"
        MISSING = "MISSING", "Missing"
        EXTRA = "EXTRA", "Extra"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction_id = models.UUIDField(null=True, blank=True)
    settlement_file_id = models.UUIDField()
    gateway_transaction_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    internal_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )
    gateway_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
    )
    difference = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )
    reconciled_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.gateway_transaction_id} - {self.status}"