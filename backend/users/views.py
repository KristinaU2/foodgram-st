from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from users.models import Subscription
from .serializers import SubscriptionSerializer

User = get_user_model()


class CustomUserViewSet(DjoserUserViewSet):
    """ViewSet пользователей с поддержкой подписок."""

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)

        if author == user:
            return Response(
                {'errors': 'Нельзя подписаться на самого себя'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if Subscription.objects.filter(user=user, author=author).exists():
            return Response(
                {'errors': 'Вы уже подписаны на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )

        Subscription.objects.create(user=user, author=author)
        serializer = SubscriptionSerializer(author, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)

        subscription = Subscription.objects.filter(user=user, author=author)
        if not subscription.exists():
            return Response(
                {'errors': 'Вы не были подписаны на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )

        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        subscriptions = User.objects.filter(subscribers__user=user)

        page = self.paginate_queryset(subscriptions)
        serializer = SubscriptionSerializer(
            page if page is not None else subscriptions,
            many=True,
            context={'request': request}
        )

        if page is not None:
            return self.get_paginated_response(serializer.data)

        return Response(serializer.data)
