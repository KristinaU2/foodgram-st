from django.contrib.auth import get_user_model
from rest_framework import serializers
from djoser.serializers import UserCreateSerializer as DjoserUserCreateSerializer, UserSerializer as DjoserUserSerializer

from users.models import Subscription
from recipes.models import Recipe
from recipes.serializers import RecipeMiniSerializer  # обязательно должен быть реализован

from recipes.models import ShoppingCart


User = get_user_model()


class UserCreateSerializer(DjoserUserCreateSerializer):
    """Сериализатор для регистрации пользователя"""
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'password')
        extra_kwargs = {'password': {'write_only': True}}


class UserSerializer(DjoserUserSerializer):
    """Сериализатор пользователя с флагом is_subscribed"""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(user=request.user, author=obj).exists()


class SubscriptionSerializer(serializers.ModelSerializer):
    """
    Сериализатор подписок:
    - отображает данные автора (подписки)
    - выводит список рецептов автора (опционально ограниченный ?recipes_limit)
    - показывает количество рецептов автора
    """
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username',
            'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(user=request.user, author=obj).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        queryset = obj.recipes.all()
        limit = request.query_params.get('recipes_limit') if request else None
        if limit and limit.isdigit():
            queryset = queryset[:int(limit)]
        return RecipeMiniSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Упрощённый рецепт для отображения в корзине/избранном."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор корзины покупок с краткой информацией о рецепте."""
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    image = serializers.ImageField(source='recipe.image', read_only=True)
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = ShoppingCart
        fields = ('id', 'name', 'image', 'cooking_time')
