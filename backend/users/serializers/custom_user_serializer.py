from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserCreateSerializer(BaseUserCreateSerializer):
    # Делаем поле обязательным, чтобы curl не ругался
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        # Явно добавляем password2 в список полей
        fields = tuple(User.REQUIRED_FIELDS) + (
            User.USERNAME_FIELD,
            'password',
            'password2',
        )

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')

        if password != password2:
            raise serializers.ValidationError({"password2": "Пароли не совпадают."})
        
        # Вызываем родительский метод валидации (он проверит сложность пароля)
        return super().validate(attrs)

    def create(self, validated_data):
        # Удаляем password2 перед отправкой в метод создания Djoser
        validated_data.pop('password2')
        return super().create(validated_data)