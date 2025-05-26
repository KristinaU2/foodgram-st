from rest_framework import serializers
from users.models import User
from literature.models import Post, Tag, FavoritePost
from drf_extra_fields.fields import Base64ImageField
from literature.models import Comment, Message



class PostMiniSerializer(serializers.ModelSerializer):
    """
    Упрощённый сериализатор публикации.
    Используется в избранном и профиле.
    """
    image = Base64ImageField()

    class Meta:
        model = Post
        fields = ('id', 'title', 'image', 'created_at')


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов (жанры, темы)."""

    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']


class PostReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения публикации."""
    author = serializers.StringRelatedField(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'author', 'title', 'content', 'image',
            'tags', 'created_at', 'is_favorited'
        ]

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.favorited_by.filter(user=request.user).exists()


class PostWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления публикации."""
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    image = Base64ImageField(required=False)

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'content', 'image', 'tags'
        ]

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        post = Post.objects.create(
            author=self.context['request'].user,
            **validated_data
        )
        post.tags.set(tags)
        return post

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if tags is not None:
            instance.tags.set(tags)

        return instance

    def to_representation(self, instance):
        return PostReadSerializer(instance, context=self.context).data


class FavoritePostSerializer(serializers.ModelSerializer):
    """Сериализатор для избранных публикаций."""
    post = PostMiniSerializer(read_only=True)

    class Meta:
        model = FavoritePost
        fields = ['post']
        read_only_fields = ['post']


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'content', 'created_at']
        read_only_fields = ['id', 'author', 'created_at']


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.StringRelatedField(read_only=True)
    recipient = serializers.PrimaryKeyRelatedField(read_only=False, queryset=User.objects.all())

    class Meta:
        model = Message
        fields = ['id', 'sender', 'recipient', 'content', 'created_at']
        read_only_fields = ['id', 'sender', 'created_at']