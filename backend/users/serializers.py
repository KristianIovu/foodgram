from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from recipes.serializers.recipe_serializers import (Base64ImageField,
                                                    ShortRecipeSerializer)

from .models import Follow

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения данных пользователя."""
    avatar = Base64ImageField(source='image', required=False, allow_null=True)

    class Meta:
        model = User
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'avatar')


class CustomUserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации новых пользователей."""
    password = serializers.CharField(write_only=True,
                                     validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=False)
    avatar = Base64ImageField(source='image', required=False, allow_null=True)

    class Meta:
        model = User
        fields = ('email',
                  'username',
                  'first_name',
                  'last_name',
                  'password',
                  'password2',
                  'avatar')
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate(self, attrs):
        """Проверяет соответсвие паролей."""
        password2 = attrs.get('password2')
        if password2 and attrs['password'] != password2:
            raise serializers.ValidationError(
                {'password2': 'Пароли не совпадают'}
            )
        return attrs

    def create(self, validated_data):
        """Создает нового пользователя."""
        validated_data.pop('password2', None)
        return User.objects.create_user(**validated_data)


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения подписок с рецептами авторов."""
    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    avatar = Base64ImageField(source='author.image', required=False,
                              allow_null=True)
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ('id',
                  'email',
                  'username',
                  'first_name',
                  'last_name',
                  'avatar',
                  'recipes_count',
                  'recipes')

    def get_recipes_count(self, obj):
        """Возвращает кол-во рецептов автора."""
        return obj.author.recipes.count()

    def get_recipes(self, obj):
        """Возвращает последние 3 рецепта автора."""
        recipes = obj.author.recipes.all()[:3]
        return ShortRecipeSerializer(recipes, many=True).data


class UserPasswordSerializer(serializers.Serializer):
    """Сериализатор для смены пароля."""
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password]
    )
    current_password = serializers.CharField(required=True)

    def validate_current_password(self, value):
        """Проверяет корректность текущего пароля."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Текущий пароль неверен')
        return value

    def save(self, **kwargs):
        """Сохраняет новый пароль пользователя."""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления аватара пользователя."""
    avatar = Base64ImageField(source='image', required=False, allow_null=True)

    class Meta:
        model = User
        fields = ('avatar',)
