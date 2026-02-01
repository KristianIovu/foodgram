from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import Follow
from .serializers import (
    AvatarSerializer,
    UserSerializer,
    FollowSerializer
)

User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    """
    Кастомный класс для пользователей, расширающий Djoser.
    Добавляет функционал подписок и управления профилем.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        """Возвращает данные текущего пользователя."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['put', 'delete'],
        url_path='me/avatar',
        permission_classes=[IsAuthenticated]
    )
    def avatar(self, request):
        """Загружает/удаляет аватар текущего пользователя."""
        user = request.user

        if request.method == 'DELETE':
            if user.avatar:
                user.avatar.delete(save=False)
            user.avatar = None
            user.save(update_fields=['avatar'])
            return Response(status=status.HTTP_204_NO_CONTENT)

        serializer = AvatarSerializer(
            user, data=request.data, partial=True, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        """
        Возвращает список подписок текущего пользователя с рецептами авторов.
        """
        authors = User.objects.filter(following__user=request.user)
        page = self.paginate_queryset(authors)
        if page is not None:
            serializer = FollowSerializer(
                page,
                many=True,
                context={'request': request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = FollowSerializer(
            authors,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id=None):
        """Подписывает или отписывает текущего пользователя от автора."""
        author = get_object_or_404(User, id=id)

        if request.method == 'POST':
            if request.user == author:
                return Response(
                    {'errors': 'Нельзя подписаться на самого себя'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            follow, created = Follow.objects.get_or_create(
                user=request.user,
                author=author
            )

            if not created:
                return Response(
                    {'errors': 'Вы уже подписаны на этого автора'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = FollowSerializer(
                author,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # DELETE запрос
        deleted_count, _ = Follow.objects.filter(
            user=request.user,
            author=author
        ).delete()

        if deleted_count == 0:
            return Response(
                {'errors': 'Вы не подписаны на этого автора'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(status=status.HTTP_204_NO_CONTENT)
