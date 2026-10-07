from rest_framework.permissions import BasePermission


class IsSuperAdminOrMerchantAdmin(BasePermission):
    allowed_roles = {
        "SUPER_ADMIN",
        "MERCHANT_ADMIN",
    }

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in self.allowed_roles
        )