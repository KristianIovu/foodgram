from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Позволяет редактировать объект только автору.
    Неавторизованные пользователи могут только просматривать.
    Авторизованные пользователи могут редактировать только свои объекты.
    """
    def has_object_permission(self, request, view, obj):
        """Проверяет права доступа к конкретному объекту."""
        # Разрешаем безопасные методы всем
        if request.method in permissions.SAFE_METHODS:
            return True
        # Для остальных методов проверяем, является ли пользователь автором
        return obj.author == request.user
