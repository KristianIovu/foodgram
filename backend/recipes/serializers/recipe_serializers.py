import base64
import uuid

from django.core.files.base import ContentFile
from rest_framework import serializers

from ..models import Recipe, RecipeIngredient, Tag
from .base_serializers import TagSerializer


class Base64ImageField(serializers.ImageField):
    """Кастомное поле для обработки изображений в формате base64."""

    def to_internal_value(self, data):
        """Преобразует строку base64 в файл изображения."""
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]
            data = ContentFile(base64.b64decode(imgstr),
                               name=f"{uuid.uuid4()}.{ext}")
        return super().to_internal_value(data)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для связи рецепта и ингредиента с количеством."""

    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецептов (GET - запросы.)"""

    author = serializers.SerializerMethodField()
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

    def get_author(self, obj):
        """Получить сериализованные данные автора рецепта."""
        from users.serializers import UserSerializer
        return UserSerializer(obj.author).data

    def get_is_favorited(self, obj):
        """Проверить, добавлен ли рецепт в избранное текущим пользователем."""
        user = self.context.get('request').user
        if user.is_authenticated:
            return user.favorites.filter(recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        """Проверка, добавлен ли рецепт в список покупок текущим польз."""
        user = self.context.get('request').user
        if user.is_authenticated:
            return user.shopping_cart.filter(recipe=obj).exists()
        return False

    def get_image(self, obj):
        """Получить URL изображения рецепта."""
        if obj.image:
            return obj.image.url
        return None


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления рецептов (POST/PATCH-запросы.)"""

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

    def validate_ingredients(self, value):
        """
        Валидация списка ингредиентов.

        Проверяет:
        1. Наличие хотя бы одного ингредиента
        2. Отсутствие дубликатов ингредиентов
        3. Корректность количества (не менее 1)
        """
        if not value:
            raise serializers.ValidationError(
                'Добавьте хотя бы один ингредиент'
            )

        ingredient_ids = [item['ingredient']['id'] for item in value]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                'Ингредиенты не должны повторяться'
            )

        for item in value:
            if item['amount'] < 1:
                raise serializers.ValidationError(
                    'Количество должно быть не менее 1'
                )
        return value

    def validate_tags(self, value):
        """
        Валидация списка тегов.

        Проверяет:
        1. Наличие хотя бы одного тега
        2. Отсутствие дубликатов тегов
        """
        if not value:
            raise serializers.ValidationError(
                'Добавьте хотя бы один тег'
            )

        if len(value) != len(set(value)):
            raise serializers.ValidationError(
                'Теги не должны повторяться'
            )
        return value

    def validate_cooking_time(self, value):
        """Валидация времени приготовления (не менее 1 минуты)."""
        if value < 1:
            raise serializers.ValidationError(
                'Время приготовления должно быть не менее 1 минуты'
            )
        return value

    def create_ingredients(self, recipe, ingredients):
        """Создать связи рецепта с ингредиентами."""
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=recipe,
                ingredient_id=item['ingredient']['id'],
                amount=item['amount']
            ) for item in ingredients
        ])

    def create(self, validated_data):
        """Создать новый рецепт."""
        validated_data.pop("author", None)
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        recipe = Recipe.objects.create(
            author=self.context['request'].user,
            **validated_data
        )

        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)

        return recipe

    def update(self, instance, validated_data):
        """Обновить существующий рецепт."""
        ingredients = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if tags is not None:
            instance.tags.set(tags)

        if ingredients is not None:
            instance.recipe_ingredients.all().delete()
            self.create_ingredients(instance, ingredients)

        instance.save()
        return instance

    def to_representation(self, instance):
        """Вернуть данные в формате RecipeReadSerializer после сохранения."""
        return RecipeReadSerializer(
            instance,
            context=self.context
        ).data


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сокращенный сериализатор рецепта (для подписок, избранного)."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

    def get_image(self, obj):
        """Получить URL изображения рецепта."""
        if obj.image:
            return obj.image.url
        return None
