from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken


class GatewayUser:
    def __init__(self, user_id):
        self.id = user_id
        self.pk = user_id
        self.is_authenticated = True


class GatewayJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        try:
            user_id = validated_token["user_id"]
        except KeyError:
            raise InvalidToken("Token contained no recognizable user identification")

        return GatewayUser(user_id)