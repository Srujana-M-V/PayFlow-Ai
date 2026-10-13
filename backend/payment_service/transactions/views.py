from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Transaction
from .serializers import TransactionSerializer


class TransactionListView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if not getattr(user, "organization_id", None):
            return Transaction.objects.none()

        return Transaction.objects.filter(
            organization_id=user.organization_id
        ).order_by("-initiated_at")