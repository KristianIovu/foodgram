from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import AvatarSerializer


class UserAvatarView(APIView):
    """АПИ для управления аватаром пользователя."""
    permission_classes = (IsAuthenticated,)

    def put(self, request):
        """Обновляет аватар пользователя."""
        data = request.data.copy()
        # Поддержка поля 'avatar' для совместимости с фронтендом
        if 'avatar' in data and 'image' not in data:
            data['image'] = data['avatar']

        serializer = AvatarSerializer(
            request.user,
            data=data,
            partial=True,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request):
        """Удаляет аватар пользователя."""
        user = request.user
        # Удаляет файл изображения из памяти
        if getattr(user, 'image', None):
            try:
                user.image.delete(save=False)
            except Exception:
                pass
        user.image = None
        user.save(update_fields=['image'])
        return Response(status=status.HTTP_204_NO_CONTENT)
