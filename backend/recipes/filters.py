import django_filters
from django.db.models import Q
from .models import Recipe


class RecipeFilter(django_filters.FilterSet):
    tags = django_filters.CharFilter(method='filter_tags')
    is_favorited = django_filters.BooleanFilter(method='filter_favorited')
    is_in_shopping_cart = django_filters.BooleanFilter(
        method='filter_shopping_cart'
    )
    
    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')
    
    def filter_tags(self, queryset, name, value):
        if value:
            tag_slugs = value.split(',')
            queryset = queryset.filter(tags__slug__in=tag_slugs).distinct()
        return queryset
    
    def filter_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorites__user=self.request.user)
        return queryset
    
    def filter_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset
