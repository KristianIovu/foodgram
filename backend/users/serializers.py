from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model
from djoser.serializers import SetPasswordSerializer

User = get_user_model()


class UserCreateSerializer(BaseUserCreateSerializer):
    """Кастомный сериализатор регистрации без password2"""

    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = ('id', 'email', 'username',
                 'first_name', 'last_name', 'password')

    def validate(self, attrs):
        # Убираем проверку password2
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user


class UserPasswordSerializer(SetPasswordSerializer):
    """Сериализатор для смены пароля"""
    pass
