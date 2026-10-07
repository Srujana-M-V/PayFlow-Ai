from rest_framework.permissions import BasePermission


class IsTenantUser(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.organization_id is not None
        )

    def has_object_permission(self, request, view, obj):
        return request.user.organization_id == obj.id


class IsSameTenant(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.organization_id is not None
        )

    def has_object_permission(self, request, view, obj):
        return request.user.organization_id == obj.organization_id