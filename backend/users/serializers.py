from django.contrib.auth import get_user_model
from rest_framework import serializers

from recipes.serializers.fields import Base64ImageField
from recipes.serializers.recipe_serializers import ShortRecipeSerializer

from .models import Follow

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения данных пользователя."""
    avatar = Base64ImageField(required=False, allow_null=True)
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
        """Проверяет, подписан ли текущий пользователь на автора."""
        request = self.context.get('request')
        return bool(
            request
            and request.user.is_authenticated
            and Follow.objects.filter(
                user=request.user,
                author=obj
            ).exists()
        )


class FollowSerializer(UserSerializer):
    """Сериализатор для отображения подписок с рецептами авторов."""
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = User
        fields = UserSerializer.Meta.fields + ('recipes_count', 'recipes')

    def get_recipes_count(self, obj):
        """Возвращает кол-во рецептов автора."""
        return obj.recipes.count()

    def get_recipes(self, obj):
        """Возвращает рецепты автора с учётом параметра recipes_limit."""
        request = self.context.get('request')
        recipes_limit = (
            request.query_params.get('recipes_limit')
            if request
            else None
        )

        recipes = obj.recipes.all()
        if recipes_limit and recipes_limit.isdigit():
            recipes = recipes[:int(recipes_limit)]
        else:
            recipes = recipes[:3]
        return ShortRecipeSerializer(recipes, many=True,
                                     context=self.context).data


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления аватара пользователя."""
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)

    def validate(self, attrs):
        """Проверяем, что поле avatar присутствует в данных."""
        if 'avatar' not in attrs:
            raise serializers.ValidationError(
                {'avatar': ['Это поле обязательно.']}
            )
        return attrs

    def to_representation(self, instance):
        return {"avatar": instance.avatar.url if instance.avatar else None}
