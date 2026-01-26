from django.contrib import admin

from .models import (Favorite,
                     Ingredient,
                     Recipe,
                     RecipeIngredient,
                     ShoppingCart,
                     Tag)


class RecipeIngredientInline(admin.TabularInline):
    """Админка для отображения ингредиентов рецепта."""
    model = RecipeIngredient
    extra = 1
    min_num = 1


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Интерфейс для управления тегами."""
    list_display = ('id', 'name', 'slug')
    list_filter = ('name',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Интерфейс для управления ингредиентами."""
    list_display = ('id', 'name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Интерфейс для управления рецептами."""
    list_display = ('id',
                    'name',
                    'author',
                    'cooking_time',
                    'pub_date',
                    'favorites_count')
    list_filter = ('author', 'tags', 'pub_date')
    search_fields = ('name', 'author__email', 'author__username')
    inlines = (RecipeIngredientInline,)
    readonly_fields = ('pub_date',)  # Дата публикации (не редактируется)

    def get_queryset(self, request):
        """Оптимизация запроса через select_related и prefetch_related."""
        queryset = super().get_queryset(request)
        return queryset.select_related('author').prefetch_related('tags')

    def favorites_count(self, obj):
        """Количество добавлений рецепта в избранное."""
        return obj.favorites.count()
    favorites_count.short_description = 'В избранном'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Интерфейс для управления избранными рецептами."""
    list_display = ('id', 'user', 'recipe')
    list_filter = ('user',)
    search_fields = ('user__email', 'recipe__name')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Интерфейс для управления списком покупок."""
    list_display = ('id', 'user', 'recipe')
    list_filter = ('user',)
    search_fields = ('user__email', 'recipe__name')
