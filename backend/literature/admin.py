from django.contrib import admin
from .models import Post, Comment, Message, Tag, FavoritePost


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """
    Админка для публикаций: отображает заголовок, автора, дату.
    Позволяет фильтровать по тегам и авторам.
    """
    list_display = ('id', 'title', 'author', 'created_at')
    list_filter = ('author', 'tags')
    search_fields = ('title', 'content', 'author__username')
    ordering = ('-created_at',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Админка для комментариев к публикациям.
    """
    list_display = ('id', 'post', 'author', 'created_at')
    search_fields = ('post__title', 'author__username', 'content')
    list_filter = ('created_at',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """
    Админка для личных сообщений между пользователями.
    """
    list_display = ('id', 'sender', 'receiver', 'created_at', 'is_read')
    search_fields = ('sender__username', 'receiver__username', 'content')
    list_filter = ('is_read', 'created_at')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """
    Админка для тегов (жанры, темы).
    """
    list_display = ('id', 'name', 'color', 'slug')
    search_fields = ('name', 'slug')
    ordering = ('name',)


@admin.register(FavoritePost)
class FavoritePostAdmin(admin.ModelAdmin):
    """
    Админка для избранных публикаций.
    """
    list_display = ('id', 'user', 'post')
    list_filter = ('user',)
    search_fields = ('user__username', 'post__title')
