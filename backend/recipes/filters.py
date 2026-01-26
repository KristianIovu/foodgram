import django_filters

from .models import Recipe, Tag


class RecipeFilter(django_filters.FilterSet):
    """Фильтр для рецептов с поддержкой тегов, избранного и списка покупок."""
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    is_favorited = django_filters.CharFilter(method='filter_favorited')
    is_in_shopping_cart = django_filters.CharFilter(
        method='filter_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def _to_bool(self, value):
        """Преобразует строкове значение в булевое."""
        return str(value).lower() in ('1', 'true', 'yes')

    def filter_favorited(self, queryset, name, value):
        """Фильтрует рецепты по признаку 'В избранном'."""
        if self._to_bool(value) and self.request.user.is_authenticated:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_shopping_cart(self, queryset, name, value):
        """Фильтрует рецепты по признаку 'в списке покупок'."""
        # Если пользователь не зарегистрирован, возвращаем пустой queryset
        if self._to_bool(value) and not self.request.user.is_authenticated:
            return queryset.none()
        if self._to_bool(value):
            return queryset.filter(in_carts__user=self.request.user)
        return queryset
