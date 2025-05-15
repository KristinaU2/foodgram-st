from django.contrib import admin
from recipes.models import (
    Ingredient, Tag, Recipe, RecipeIngredient,
    Favorite, ShoppingCart
)


class IngredientInline(admin.TabularInline):
    """
    Вложенная модель ингредиентов — для отображения в рецепте.
    Позволяет сразу добавлять ингредиенты при создании рецепта.
    """
    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """
    Админка для рецептов: отображает автора, название, теги и т.д.
    Добавляет фильтры и встроенные ингредиенты.
    """
    list_display = ('id', 'name', 'author', 'cooking_time')
    list_filter = ('author', 'tags',)
    search_fields = ('name', 'author__username')
    inlines = [IngredientInline]


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админка для ингредиентов: поиск и фильтрация по имени."""
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админка для тегов: редактирование имени, цвета, слага."""
    list_display = ('id', 'name', 'color', 'slug')
    search_fields = ('name', 'slug')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Админка для избранного: кто добавил и какой рецепт."""
    list_display = ('id', 'user', 'recipe')
    list_filter = ('user',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Админка для корзины покупок: кто добавил и какой рецепт."""
    list_display = ('id', 'user', 'recipe')
    list_filter = ('user',)
