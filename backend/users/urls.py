from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .avatar import UserAvatarView
from .views import UserViewSet


router = DefaultRouter()
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    # Управление аватаром пользователя
    path('users/me/avatar/', UserAvatarView.as_view(), name='user-avatar'),
    # Аутентификация по токенам
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
