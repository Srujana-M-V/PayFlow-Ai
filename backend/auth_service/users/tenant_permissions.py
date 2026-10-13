
from rest_framework.permissions import BasePermission


class IsTenantUser(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        return (
            user
            and user.is_authenticated
            and (
                user.role == "SUPER_ADMIN"
                or user.organization_id is not None
            )
        )

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.role == "SUPER_ADMIN":
            return True

        organization_id = getattr(obj, "organization_id", None)

        if organization_id is None and hasattr(obj, "organization"):
            organization_id = getattr(obj.organization, "id", None)

        return (
            user.organization_id is not None
            and str(user.organization_id) == str(organization_id)
        )


class IsSameTenant(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        return (
            user
            and user.is_authenticated
            and user.organization_id is not None
        )

    def has_object_permission(self, request, view, obj):
        organization_id = getattr(obj, "organization_id", None)

        if organization_id is None and hasattr(obj, "organization"):
            organization_id = getattr(obj.organization, "id", None)

        return (
            request.user.organization_id is not None
            and str(request.user.organization_id) == str(organization_id)
        )
