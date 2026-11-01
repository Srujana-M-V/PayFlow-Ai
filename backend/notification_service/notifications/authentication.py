from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import (
    JWTStatelessUserAuthentication,
)
from rest_framework_simplejwt.models import TokenUser


class PayFlowTokenUser(TokenUser):

    def __init__(self, token):
        super().__init__(token)

        self.organization_id = token.get("organization_id")
        self.role = token.get("role")


class PayFlowJWTAuthentication(JWTStatelessUserAuthentication):

    def get_user(self, validated_token):

        user_id = validated_token.get("user_id")
        organization_id = validated_token.get("organization_id")

        if not user_id:
            raise AuthenticationFailed(
                "User ID missing from authentication token."
            )

        if not organization_id:
            raise AuthenticationFailed(
                "Organization ID missing from authentication token."
            )

        return PayFlowTokenUser(validated_token)