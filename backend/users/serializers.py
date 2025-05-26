from django.contrib.auth import get_user_model
from rest_framework import serializers
from djoser.serializers import UserCreateSerializer as DjoserUserCreateSerializer, UserSerializer as DjoserUserSerializer

from users.models import Subscription
from literature.models import Post
from literature.serializers import PostMiniSerializer  # упрощённый сериализатор публикации

User = get_user_model()


class UserCreateSerializer(DjoserUserCreateSerializer):
    """Сериализатор для регистрации пользователя."""
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'password')
        extra_kwargs = {'password': {'write_only': True}}


class UserSerializer(DjoserUserSerializer):
    """Сериализатор пользователя с флагом подписки."""
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
    - выводит данные автора
    - список публикаций автора (ограниченный ?posts_limit)
    - количество публикаций
    """
    is_subscribed = serializers.SerializerMethodField()
    posts = serializers.SerializerMethodField()
    posts_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username',
            'first_name', 'last_name',
            'is_subscribed', 'posts', 'posts_count'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(user=request.user, author=obj).exists()

    def get_posts(self, obj):
        request = self.context.get('request')
        queryset = obj.posts.all()  # related_name='posts' в модели Post
        limit = request.query_params.get('posts_limit') if request else None
        if limit and limit.isdigit():
            queryset = queryset[:int(limit)]
        return PostMiniSerializer(queryset, many=True).data

    def get_posts_count(self, obj):
        return obj.posts.count()
