from django.db import transaction
from rest_framework import serializers

from recipes.models import Ingredient
from ..models import Recipe, RecipeIngredient, Tag
from .base_serializers import TagSerializer
from .fields import Base64ImageField

class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для связи рецепта и ингредиента с количеством."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient'
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецептов (GET - запросы.)"""

    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredients',
        many=True
    )
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')
    
    def get_fields(self):
        fields = super().get_fields()
        from users.serializers import UserSerializer
        fields['author'] = UserSerializer(read_only=True)
        return fields

    def get_is_favorited(self, obj):
        """Проверить, добавлен ли рецепт в избранное текущим пользователем."""
        request = self.context.get('request')
        return bool(
            request
            and request.user.is_authenticated
            and request.user.favorite_set.filter(recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        """Проверка, добавлен ли рецепт в список покупок текущим польз."""
        request = self.context.get('request')
        return bool(
            request
            and request.user.is_authenticated
            and request.user.shoppingcart_set.filter(recipe=obj).exists()
        )

    def get_image(self, obj):
        """Получить URL изображения рецепта."""
        if obj.image:
            return obj.image.url
        return None


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Создание и обновление рецептов (POST/PATCH-запросы.)"""

    ingredients = RecipeIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time')

    def validate(self, data):
        """Валидация тегов и ингредиентов для создания и редактирования."""
        if 'tags' not in data or not data['tags']:
            raise serializers.ValidationError(
                {'tags': ['Добавьте хотя бы один тег.']}
            )

        tags = data['tags']
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                {'tags': ['Теги не должны повторяться.']}
            )

        if 'ingredients' not in data or not data['ingredients']:
            raise serializers.ValidationError(
                {'ingredients': ['Добавьте хотя бы один ингредиент.']}
            )

        ingredients = data['ingredients']
        ingredient_ids = [item['ingredient'].id for item in ingredients]

        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                {'ingredients': ['Ингредиенты не должны повторяться.']}
            )

        return data

    def create_ingredients(self, recipe, ingredients):
        """Создать связи рецепта с ингредиентами."""
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=recipe,
                ingredient=item['ingredient'],
                amount=item['amount']
            ) for item in ingredients
        ])

    @transaction.atomic
    def create(self, validated_data):
        """Создать новый рецепт."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        recipe = Recipe.objects.create(
            author=self.context['request'].user,
            **validated_data
        )

        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)

        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        """Обновить существующий рецепт."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        instance.tags.clear()
        instance.tags.set(tags)

        instance.recipe_ingredients.all().delete()
        # Для этой связи метод clear() не работает,
        # поэтому удаляем старые ингредиенты через delete().
        self.create_ingredients(instance, ingredients)

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """Вернуть данные в формате RecipeReadSerializer после сохранения."""
        return RecipeReadSerializer(
            instance,
            context=self.context
        ).data


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сокращенный сериализатор рецепта (для подписок, избранного)."""
    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

    def get_image(self, obj):
        """Получить URL изображения рецепта."""
        if obj.image:
            return obj.image.url
        return None
