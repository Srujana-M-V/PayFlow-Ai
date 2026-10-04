from django.db import models


class GatewayHealth(models.Model):
    gateway = models.ForeignKey(
        "gateways.GatewayConfig",
        on_delete=models.CASCADE,
        related_name="health_records",
    )
    success_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
    )
    average_response_time = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    total_requests = models.PositiveIntegerField(default=0)
    successful_requests = models.PositiveIntegerField(default=0)
    failed_requests = models.PositiveIntegerField(default=0)
    health_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
    )
    last_checked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.gateway.name} - {self.health_score}"