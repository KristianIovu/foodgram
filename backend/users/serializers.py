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
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'avatar',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        """Проверяет, подписан ли текущий пользователь на автора (obj)."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Follow.objects.filter(
                user=request.user, 
                author=obj
            ).exists()
        return False


class CustomUserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации новых пользователей."""
    password = serializers.CharField(write_only=True,
                                     validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=False)
    avatar = Base64ImageField(source='image',
                              required=False,
                              allow_null=True,
                              write_only=True)

    class Meta:
        model = User
        fields = ('email',
                  'id',
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
        """Проверяет соответствие паролей, если password2 предоставлен."""
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

    def to_representation(self, instance):
        """Возвращаем представление без поля avatar."""
        representation = super().to_representation(instance)
        representation.pop('avatar', None)
        return representation


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения подписок с рецептами авторов."""
    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    avatar = Base64ImageField(source='author.image', required=False,
                              allow_null=True)
    is_subscribed = serializers.SerializerMethodField()
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
                  'is_subscribed',
                  'recipes_count',
                  'recipes')

    def get_recipes_count(self, obj):
        """Возвращает кол-во рецептов автора."""
        return obj.author.recipes.count()

    def get_recipes(self, obj):
        """Возвращает рецепты автора с учётом параметра recipes_limit."""
        request = self.context.get('request')
        recipes_limit = (
            request.query_params.get('recipes_limit')
            if request 
            else None
        )

        recipes = obj.author.recipes.all()
        if recipes_limit and recipes_limit.isdigit():
            recipes = recipes[:int(recipes_limit)]
        else:
            recipes = recipes[:3]
        return ShortRecipeSerializer(recipes, many=True).data

    def get_is_subscribed(self, obj):
        """Всегда True, т.к. это serializer для подписок."""
        return True

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
    avatar = Base64ImageField(source='image')

    class Meta:
        model = User
        fields = ('avatar',)

    def validate(self, attrs):
        """Проверяем, что поле avatar присутствует в данных."""
        if 'image' not in attrs:
            raise serializers.ValidationError(
                {'avatar': ['Это поле обязательно.']}
            )
        return attrs

    def to_representation(self, instance):
        return {"avatar": instance.image.url if instance.image else None}
