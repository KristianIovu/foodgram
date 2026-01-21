from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserCreateSerializer(BaseUserCreateSerializer):
    """Кастомный сериализатор без password2"""
    
    password2 = serializers.CharField(write_only=True, required=False)
    
    class Meta(BaseUserCreateSerializer.Meta):
        fields = ('id', 'email', 'username', 
                 'first_name', 'last_name', 'password')
    
    def validate(self, attrs):
        # Игнорируем password2 если он есть
        attrs.pop('password2', None)
        return attrs
