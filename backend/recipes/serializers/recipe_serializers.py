from rest_framework import serializers
from django.core.validators import MinValueValidator
from django.shortcuts import get_object_or_404
from ..models import Recipe, RecipeIngredient, Tag, Ingredient
from .base_serializers import TagSerializer, IngredientSerializer


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    
    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
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
        from users.serializers import UserSerializer
        return UserSerializer(obj.author).data
    
    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return user.favorites.filter(recipe=obj).exists()
        return False
    
    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return user.shopping_cart.filter(recipe=obj).exists()
        return False
    
    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return None


class RecipeWriteSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    image = serializers.ImageField(required=True)
    
    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time')
    
    def validate_ingredients(self, value):
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
        if value < 1:
            raise serializers.ValidationError(
                'Время приготовления должно быть не менее 1 минуты'
            )
        return value
    
    def create_ingredients(self, recipe, ingredients):
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=recipe,
                ingredient_id=item['ingredient']['id'],
                amount=item['amount']
            ) for item in ingredients
        ])
    
    def create(self, validated_data):
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
        return RecipeReadSerializer(
            instance,
            context=self.context
        ).data


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
    
    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return None
