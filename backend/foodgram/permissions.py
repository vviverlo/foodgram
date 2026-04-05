from rest_framework.permissions import SAFE_METHODS, BasePermission


class UserDetailPermission(BasePermission):
    """GET — всем; изменение профиля — только владельцу."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and obj.pk == request.user.pk
