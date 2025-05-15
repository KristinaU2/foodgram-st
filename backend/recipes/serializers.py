from rest_framework import serializers
from users.models import User
from recipes.models import (
    Ingredient,
    Tag,
    Recipe,
    RecipeIngredient,
    Favorite,
    ShoppingCart,
)
from drf_extra_fields.fields import Base64ImageField  # если будешь передавать картинки в base64


class RecipeMiniSerializer(serializers.ModelSerializer):
    """
    Упрощённый сериализатор рецептов:
    используется в подписках.
    """
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для отдельного ингредиента."""

    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тега."""

    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения ингредиента внутри рецепта."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source='ingredient'
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'name', 'measurement_unit', 'amount']


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецепта (GET-запросы)."""
    author = serializers.StringRelatedField(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = serializers.SerializerMethodField()
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            'id', 'author', 'name', 'image', 'text',
            'ingredients', 'tags', 'cooking_time', 'created_at',
            'is_favorited', 'is_in_shopping_cart'
        ]

    def get_ingredients(self, obj):
        """Метод для получения списка ингредиентов с количеством."""
        ingredients = RecipeIngredient.objects.filter(recipe=obj)
        return RecipeIngredientSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        """Проверяет, добавлен ли рецепт в избранное текущим пользователем."""
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.favorited_by.filter(user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        """Проверяет, добавлен ли рецепт в корзину текущим пользователем."""
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.in_shopping_cart.filter(user=request.user).exists()


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления рецептов."""
    ingredients = RecipeIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = [
            'id', 'name', 'image', 'text', 'ingredients', 'tags', 'cooking_time'
        ]

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError('Нужно добавить хотя бы один ингредиент.')
        seen = set()
        for item in value:
            ingredient_id = item['ingredient'].id
            if ingredient_id in seen:
                raise serializers.ValidationError('Ингредиенты должны быть уникальными.')
            seen.add(ingredient_id)
        return value

    def create_ingredients(self, recipe, ingredients):
        """Создаёт объекты RecipeIngredient для рецепта."""
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount']
            ) for ingredient in ingredients
        ])

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=self.context['request'].user, **validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if tags is not None:
            instance.tags.set(tags)
        if ingredients is not None:
            instance.ingredients.clear()
            self.create_ingredients(instance, ingredients)

        return instance

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для избранного: возвращает мини-рецепт."""
    recipe = RecipeMiniSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = ['recipe']
        read_only_fields = ['recipe']


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для корзины: возвращает мини-рецепт."""
    recipe = RecipeMiniSerializer(read_only=True)

    class Meta:
        model = ShoppingCart
        fields = ['recipe']
        read_only_fields = ['recipe']