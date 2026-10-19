from rest_framework.permissions import BasePermission


class IsSuperAdminOrMerchantAdmin(BasePermission):
    allowed_roles = {
        "SUPER_ADMIN",
        "MERCHANT_ADMIN",
    }

    def has_permission(self, request, view):
        user = request.user

        return (
            user
            and user.is_authenticated
            and user.role in self.allowed_roles
        )


class HasTenantAccess(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user and user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.role == "SUPER_ADMIN":
            return True

        organization_id = getattr(obj, "organization_id", None)

        if organization_id is None and hasattr(obj, "organization"):
            organization_id = obj.organization_id

        return (
            user.organization_id is not None
            and str(user.organization_id) == str(organization_id)
        )