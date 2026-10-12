from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from users.permissions import IsSuperAdminOrMerchantAdmin
from users.tenant_permissions import IsTenantUser

from .models import Organization
from .serializers import OrganizationSerializer


class MerchantListCreateView(APIView):
    permission_classes = [IsSuperAdminOrMerchantAdmin]

    def get(self, request):
        if request.user.role == "SUPER_ADMIN":
            organizations = Organization.objects.all().order_by("-created_at")
        else:
            organizations = Organization.objects.filter(
                id=request.user.organization_id
            ).order_by("-created_at")

        serializer = OrganizationSerializer(organizations, many=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def post(self, request):
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


class MerchantDetailView(APIView):
    permission_classes = [IsTenantUser]

    def get(self, request, organization_id):
        try:
            organization = Organization.objects.get(id=organization_id)
        except Organization.DoesNotExist:
            return Response(
                {"detail": "Organization not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if request.user.role != "SUPER_ADMIN":
            if request.user.organization_id != organization.id:
                return Response(
                    {"detail": "You do not have access to this organization."},
                    status=status.HTTP_403_FORBIDDEN,
                )

        return Response(
            OrganizationSerializer(organization).data,
            status=status.HTTP_200_OK,
        )