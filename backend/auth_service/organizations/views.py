
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from users.permissions import IsSuperAdminOrMerchantAdmin
from .models import Organization
from .serializers import OrganizationSerializer


class OrganizationCreateView(APIView):
    permission_classes = [IsSuperAdminOrMerchantAdmin]

    def post(self, request):
        if request.user.role != "SUPER_ADMIN":
            return Response(
                {"detail": "Only super admins can create organizations."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = OrganizationSerializer(data=request.data)

        if serializer.is_valid():
            organization = serializer.save()

            return Response(
                OrganizationSerializer(organization).data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )
