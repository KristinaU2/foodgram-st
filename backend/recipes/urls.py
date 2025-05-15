from django.urls import path, include
from rest_framework.routers import DefaultRouter

from recipes.views import (
    TagViewSet,
    IngredientViewSet,
    RecipeViewSet,
)

# Роутер для автоматической генерации маршрутов
router = DefaultRouter()
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'recipes', RecipeViewSet, basename='recipes')

# Основной список URL'ов
urlpatterns = [
    path('', include(router.urls)),
]
