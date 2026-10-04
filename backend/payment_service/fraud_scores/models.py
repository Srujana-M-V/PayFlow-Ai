import uuid

from django.db import models


class FraudScore(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction_id = models.UUIDField()
    score = models.FloatField()
    velocity_score = models.FloatField(null=True, blank=True)
    geo_score = models.FloatField(null=True, blank=True)
    device_score = models.FloatField(null=True, blank=True)
    ml_score = models.FloatField(null=True, blank=True)
    triggered_rules = models.JSONField(default=list, blank=True)
    reviewed_by = models.UUIDField(null=True, blank=True)
    review_decision = models.CharField(
        max_length=20,
        null=True,
        blank=True,
    )
    scored_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_id} - {self.score}"
