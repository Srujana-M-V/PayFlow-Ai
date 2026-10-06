from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import OrganizationSerializer


class OrganizationCreateView(APIView):
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