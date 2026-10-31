from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "organization_id",
        "notification_type",
        "channel",
        "status",
        "created_at",
    )

    list_filter = (
        "notification_type",
        "channel",
        "status",
    )

    search_fields = (
        "organization_id",
        "transaction_id",
        "recipient_email",
        "event_id",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "sent_at",
    )