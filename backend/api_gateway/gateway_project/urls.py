from django.contrib import admin
from django.urls import path
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class GatewayProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(
            {
                "message": "API Gateway JWT validation successful.",
                "user_id": request.user.id,
            }
        )


urlpatterns = [
    path("admin/", admin.site.urls),
    path("protected/", GatewayProtectedView.as_view(), name="gateway-protected"),
]