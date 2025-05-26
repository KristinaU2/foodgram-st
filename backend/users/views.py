from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from users.models import Subscription
from django.contrib.auth import get_user_model
from users.serializers import UserSerializer, SubscriptionSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet

User = get_user_model()


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Вьюсет для чтения пользователей и подписки.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def subscribe(self, request, pk=None):
        author = self.get_object()
        if author == request.user:
            return Response({'detail': 'Нельзя подписаться на самого себя'}, status=400)
        obj, created = Subscription.objects.get_or_create(user=request.user, author=author)
        if not created:
            return Response({'detail': 'Вы уже подписаны'}, status=400)
        serializer = SubscriptionSerializer(author, context={'request': request})
        return Response(serializer.data, status=201)

    @subscribe.mapping.delete
    def unsubscribe(self, request, pk=None):
        author = self.get_object()
        deleted, _ = Subscription.objects.filter(user=request.user, author=author).delete()
        if not deleted:
            return Response({'detail': 'Вы не подписаны'}, status=400)
        return Response(status=204)


class SubscriptionViewSet(ListModelMixin, GenericViewSet):
    """
    Возвращает список подписок текущего пользователя.
    """
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)
