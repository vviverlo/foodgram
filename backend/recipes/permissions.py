from rest_framework.permissions import SAFE_METHODS, BasePermission


class OwnerOrReadOnly(BasePermission):
    """
    GET, HEAD, OPTIONS — всем; изменение и удаление — только автору объекта.
    Аутентификация для небезопасных методов задаётся через
    IsAuthenticatedOrReadOnly во вьюсете.
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or obj.author == request.user
        )
