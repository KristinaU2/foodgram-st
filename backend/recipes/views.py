from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.db import models
from django.http import FileResponse
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

from django.http import HttpResponse
from django.utils.encoding import smart_str

from django.db.models import Sum  # Обязательно для .annotate(total_amount=Sum('amount'))


from recipes.models import (
    Recipe, Tag, Ingredient, Favorite, ShoppingCart, RecipeIngredient
)
from recipes.serializers import (
    RecipeReadSerializer, RecipeWriteSerializer,
    TagSerializer, IngredientSerializer,
    FavoriteSerializer, ShoppingCartSerializer
)
from recipes.filters import RecipeFilter


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Просмотр тегов — доступен всем пользователям."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Просмотр ингредиентов с фильтрацией по началу имени."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        name = self.request.query_params.get('name')
        if name:
            return self.queryset.filter(name__istartswith=name)
        return self.queryset


class RecipeViewSet(viewsets.ModelViewSet):
    """CRUD для рецептов, избранное, корзина, экспорт PDF и генерация ссылок."""
    queryset = Recipe.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def get_permissions(self):
        if self.request.method in ['POST', 'PATCH', 'DELETE']:
            return [IsAuthenticated()]
        return [AllowAny()]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        """Добавление или удаление рецепта из избранного."""
        recipe = get_object_or_404(Recipe, pk=pk)

        if request.method == 'POST':
            obj, created = Favorite.objects.get_or_create(user=request.user, recipe=recipe)
            if not created:
                return Response({'error': 'Рецепт уже в избранном'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = FavoriteSerializer(obj, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        deleted, _ = Favorite.objects.filter(user=request.user, recipe=recipe).delete()
        if deleted:
            return Response({'status': 'Удалено из избранного'}, status=status.HTTP_204_NO_CONTENT)
        return Response({'error': 'Рецепт не найден в избранном'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        """Добавляет или удаляет рецепт из корзины текущего пользователя."""
        recipe = get_object_or_404(Recipe, pk=pk)

        if request.method == 'POST':
            cart_item, created = ShoppingCart.objects.get_or_create(user=request.user, recipe=recipe)
            if not created:
                return Response({'error': 'Рецепт уже в корзине'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = ShoppingCartSerializer(cart_item, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        deleted, _ = ShoppingCart.objects.filter(user=request.user, recipe=recipe).delete()
        if deleted:
            return Response({'status': 'Удалено из корзины'}, status=status.HTTP_204_NO_CONTENT)
        return Response({'error': 'Рецепт не найден в корзине'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def get_link(self, request, pk=None):
        """Возвращает публичную ссылку на рецепт (для шаринга на фронтенде)."""
        recipe = get_object_or_404(Recipe, pk=pk)
        link = f'http://127.0.0.1:3000/recipes/{recipe.id}/'
        return Response({'link': link}, status=status.HTTP_200_OK)
    
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        """
        Генерирует текстовый файл со списком покупок пользователя и отправляет его в ответе.
        """
        ingredients = (
            RecipeIngredient.objects
            .filter(recipe__in_shopping_cart__user=request.user)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(total_amount=Sum('amount'))
            .order_by('ingredient__name')
        )

        lines = ["Список покупок:\n"]

        if not ingredients:
            lines.append("Корзина пуста.\n")
        else:
            for index, item in enumerate(ingredients, start=1):
                lines.append(
                    f"{index}. {item['ingredient__name']} — {item['total_amount']} {item['ingredient__measurement_unit']}\n"
                )

        content = ''.join(lines)
        response = HttpResponse(content, content_type='text/plain; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="shopping_cart.txt"'
        return response