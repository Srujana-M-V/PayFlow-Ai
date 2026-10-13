from rest_framework import serializers

from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            "id",
            "organization_id",
            "order_id",
            "amount",
            "currency",
            "status",
            "gateway_used",
            "gateway_txn_id",
            "fraud_score",
            "fraud_action",
            "initiated_at",
            "completed_at",
        ]
        read_only_fields = fields