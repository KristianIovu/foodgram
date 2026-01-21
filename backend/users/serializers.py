from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения информации о пользователе."""
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name')

class CustomUserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации (без поля password2)."""
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'password')

    def create(self, validated_data):
        # Хешируем пароль перед сохранением в базу
        return User.objects.create_user(**validated_data)