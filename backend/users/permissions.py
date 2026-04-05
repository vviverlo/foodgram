from rest_framework.permissions import SAFE_METHODS, BasePermission


class ReadOnlyOrCurrentUserOrAdmin(BasePermission):
    """
    Безопасные методы (GET, HEAD, OPTIONS) — всем, в т.ч. анонимам.
    PATCH, PUT, DELETE — только сам пользователь или админ.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        user = request.user
        return user.is_staff or obj.pk == user.pk
