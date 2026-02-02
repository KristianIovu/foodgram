from django_filters import rest_framework as filters
import django_filters

from .models import Ingredient, Recipe, Tag


class IngredientFilter(filters.FilterSet):
    """Фильтр для ингредиентов."""

    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ['name']


class RecipeFilter(django_filters.FilterSet):
    """Фильтр для рецептов с поддержкой тегов, избранного и списка покупок."""
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    is_favorited = filters.NumberFilter(method='filter_favorited')
    is_in_shopping_cart = filters.NumberFilter(method='filter_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def filter_favorited(self, queryset, name, value):
        """Фильтрует рецепты по признаку 'В избранном'."""
        if int(value) == 1:
            if self.request.user.is_authenticated:
                return queryset.filter(favorite_set__user=self.request.user)
            return queryset.none()
        return queryset

    def filter_shopping_cart(self, queryset, name, value):
        """Фильтрует рецепты по признаку 'в списке покупок'."""
        # Если пользователь не зарегистрирован, возвращаем пустой queryset
        if int(value) == 1:
            if self.request.user.is_authenticated:
                return queryset.filter(shoppingcart_set__user=self.request.user)
            return queryset.none()
        return queryset
