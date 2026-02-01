from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import UserViewSet


router = DefaultRouter()
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    # Подписки
    path('users/subscriptions/',
         UserViewSet.as_view({'get': 'subscriptions'}),
         name='user-subscriptions'),
    # Аутентификация по токенам
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
