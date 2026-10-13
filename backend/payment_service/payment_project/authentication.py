from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken


class GatewayUser:
    def __init__(self, user_id, organization_id=None, role=None):
        self.id = user_id
        self.pk = user_id
        self.organization_id = organization_id
        self.role = role
        self.is_authenticated = True


class GatewayJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        try:
            user_id = validated_token["user_id"]
        except KeyError:
            raise InvalidToken(
                "Token contained no recognizable user identification"
            )

        organization_id = validated_token.get("organization_id")
        role = validated_token.get("role")

        return GatewayUser(
            user_id=user_id,
            organization_id=organization_id,
            role=role,
        )