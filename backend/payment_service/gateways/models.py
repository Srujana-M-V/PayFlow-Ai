from django.db import models


class GatewayConfig(models.Model):
    name = models.CharField(max_length=100)
    provider = models.CharField(max_length=100)
    api_base_url = models.URLField()
    api_key = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    priority = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name