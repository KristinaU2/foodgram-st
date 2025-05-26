from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from literature.models import Post, Tag, FavoritePost
from .serializers import (
    PostReadSerializer,
    PostWriteSerializer,
    TagSerializer,
    FavoritePostSerializer,
)
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from literature.models import Comment, Message
from literature.serializers import CommentSerializer, MessageSerializer
from rest_framework.permissions import IsAuthenticated


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            return PostWriteSerializer
        return PostReadSerializer

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk=None):
        post = self.get_object()
        favorite, created = FavoritePost.objects.get_or_create(user=request.user, post=post)
        if not created:
            return Response({'detail': 'Уже в избранном'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = FavoritePostSerializer(favorite)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def remove_favorite(self, request, pk=None):
        post = self.get_object()
        deleted, _ = FavoritePost.objects.filter(user=request.user, post=post).delete()
        if not deleted:
            return Response({'detail': 'Публикация не в избранном'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]


class CommentViewSet(viewsets.ModelViewSet):
    """
    CRUD для комментариев к публикациям.
    Поддерживает фильтрацию по ?post={post_id}
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Comment.objects.all()
        post_id = self.request.query_params.get('post')
        if post_id:
            queryset = queryset.filter(post__id=post_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class MessageViewSet(viewsets.ModelViewSet):
    """
    Личные сообщения между пользователями.
    Поддерживает фильтрацию по ?recipient={id}
    """
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Message.objects.filter(sender=user) | Message.objects.filter(recipient=user)
        recipient_id = self.request.query_params.get('recipient')
        if recipient_id:
            queryset = queryset.filter(recipient__id=recipient_id)
        return queryset.distinct()

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)
