from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet

# Создаем router для UserViewSet
router = DefaultRouter()
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
