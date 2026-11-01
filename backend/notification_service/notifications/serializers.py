from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = "__all__"

        read_only_fields = (
            "id",
            "organization_id",
            "user_id",
            "status",
            "retry_count",
            "max_retries",
            "error_message",
            "created_at",
            "updated_at",
            "sent_at",
        )