from rest_framework import serializers

from django.contrib.auth import get_user_model
from recipes.serializers.recipe_serializers import ShortRecipeSerializer

from ..models import Follow

User = get_user_model()


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок с рецептами авторов."""
    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = (
            'id', 'email', 'username', 'first_name',
            'last_name', 'recipes_count', 'recipes'
        )

    def get_recipes_count(self, obj):
        """Возвращает количество рецептов автора."""
        return obj.author.recipes.count()

    def get_recipes(self, obj):
        """Возвращает последние 3 рецепта автора.
        """
        recipes = obj.author.recipes.all()[:3]
        return ShortRecipeSerializer(recipes, many=True).data
