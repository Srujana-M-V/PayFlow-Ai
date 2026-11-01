from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError

from .models import Notification
from .serializers import NotificationSerializer


class NotificationListCreateView(generics.ListCreateAPIView):

    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        organization_id = self.request.user.organization_id

        if not organization_id:
            return Notification.objects.none()

        return Notification.objects.filter(
            organization_id=organization_id
        ).order_by("-created_at")

    def perform_create(self, serializer):
        user = self.request.user

        if not user.organization_id:
            raise ValidationError(
                "User is not associated with an organization."
            )

        serializer.save(
            organization_id=user.organization_id,
            user_id=user.id,
        )


class NotificationDetailView(generics.RetrieveAPIView):

    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        organization_id = self.request.user.organization_id

        if not organization_id:
            return Notification.objects.none()

        return Notification.objects.filter(
            organization_id=organization_id
        )