from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from .filters import RecipeFilter, IngredientFilter
from .models import RecipeIngredient
from .models import (
    Recipe,
    Tag,
    Ingredient,
    Favorite,
    ShoppingCart
)
from .permissions import IsAuthorOrReadOnly
from .serializers.base_serializers import TagSerializer, IngredientSerializer
from .serializers.recipe_serializers import (
    RecipeReadSerializer,
    RecipeWriteSerializer,
    ShortRecipeSerializer,
)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Работа с тегами.

    Доступен только для чтения.
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Для работы с ингредиентами.

    Есть поиск по началу названия через параметр 'name'.
    """

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    """Для работы с рецептами."""

    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)

    def get_serializer_class(self):
        """Выбирает сериализатор в зависимости от действия."""
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        """Сохраняет рецепт с указанием автора."""
        serializer.save(author=self.request.user)

    def partial_update(self, request, *args, **kwargs):
        """Частичное обновление рецепта."""
        instance = self.get_object()

        serializer = RecipeWriteSerializer(
            instance,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(
            RecipeReadSerializer(
                instance,
                context={'request': request}
            ).data,
            status=status.HTTP_200_OK
        )

    def _manage_user_recipe_relation(self,
                                     request,
                                     pk,
                                     model_class,
                                     error_messages):
        """Вспомогательный метод для управления связями пользователь-рецепт."""
        recipe = get_object_or_404(Recipe, pk=pk)

        if request.method == 'POST':
            obj, created = model_class.objects.get_or_create(
                user=request.user,
                recipe=recipe
            )

            if not created:
                return Response(
                    {'errors': error_messages['exists']},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = ShortRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        deleted_count, _ = model_class.objects.filter(
            user=request.user,
            recipe=recipe
        ).delete()

        if deleted_count == 0:
            return Response(
                {'errors': error_messages['not_exists']},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        """Удаляет или добавляет рецепт из избранного."""
        return self._manage_user_recipe_relation(
            request=request,
            pk=pk,
            model_class=Favorite,
            error_messages={
                'exists': 'Рецепт уже в избранном',
                'not_exists': 'Рецепта нет в избранном'
            }
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        """Добавляет или удаляет рецепт из списка покупок."""
        return self._manage_user_recipe_relation(
            request=request,
            pk=pk,
            model_class=ShoppingCart,
            error_messages={
                'exists': 'Рецепт уже в списке покупок',
                'not_exists': 'Рецепта нет в списке покупок'
            }
        )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        """Скачивает текстовый файл со списком покупок."""
        user = request.user

        ingredients = RecipeIngredient.objects.filter(
            recipe__in_carts__user=user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(
            total_amount=Sum('amount')
        ).order_by('ingredient__name')

        return self._create_shopping_list_response(ingredients)

    def _create_shopping_list_response(self, ingredients):
        """Создает HttpResponse с файлом списка покупок."""
        shopping_list = []
        shopping_list.append('Список покупок\n')
        shopping_list.append('=' * 50 + '\n')

        for item in ingredients:
            name = item['ingredient__name']
            unit = item['ingredient__measurement_unit']
            amount = item['total_amount']
            shopping_list.append(f'{name} ({unit}) - {amount}\n')

        shopping_list.append('\n' + '=' * 50)
        shopping_list.append('\nПриятного аппетита!')

        response = HttpResponse(
            ''.join(shopping_list),
            content_type='text/plain; charset=utf-8'
        )
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )

        return response

    @action(
        detail=True,
        methods=['get'],
        url_path='get-link'
    )
    def get_link(self, request, pk=None):
        """Возвращает короткую ссылку на рецепт."""
        recipe = self.get_object()
        url = request.build_absolute_uri(recipe.get_absolute_url())
        return Response({'short-link': url})
